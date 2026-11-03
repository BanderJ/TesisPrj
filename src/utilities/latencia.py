"""
Medidor de latencia del pipeline completo.

Evidencia del indicador de tesis (Objetivo específico 4, Resultado 01):
    "Latencia de comunicación <= 200 ms entre captura, procesamiento y registro
     en al menos 50 iteraciones consecutivas."

Una iteración = un frame que recorrió todo el camino hasta quedar registrado.
Tramos medidos (total_ms = espera + procesamiento + decision, exacto):

    espera_ms         ts de captura -> el hilo del tracker toma el frame
    procesamiento_ms  YOLO sobre los tiles (un solo batch)
    decision_ms       ByteTrack + resolución de clase + solicitud al servo + conteo
    total_ms          captura -> registro

DEFINICIONES OPERATIVAS (declararlas en la metodología de la tesis):

1. "Registro" = el conteo del lote quedó actualizado en memoria y el grano ya
   pidió separación. NO es el INSERT en PostgreSQL: la persistencia ocurre una
   vez por lote en /evaluacion/{id}/finalizar, no por frame.

2. El total NO incluye SERVO_DELAY_S. Ese medio segundo es el viaje físico del
   grano de la cámara al separador: espera programada para sincronizar con el
   transporte, no cómputo. Incluirlo mediría la velocidad de la faja.
   Por eso esto es latencia de DECISIÓN, no de actuación. El requerimiento no
   funcional que pide "<= 200 ms entre detección y actuación" se responde con
   esta cifra más la declaración de que la actuación se sincroniza a propósito
   con el avance de la faja.
"""
import csv
import os
import statistics
import threading
import time
from collections import deque

from src.config import Config

# Tramos en el orden en que ocurren; define también el orden de columnas del CSV.
TRAMOS: tuple[str, ...] = ("espera_ms", "procesamiento_ms", "decision_ms", "total_ms")

# Raíz del proyecto: src/utilities/latencia.py -> ../../..
# Anclar aquí evita que ML_LATENCIA_DIR relativo dependa del CWD desde donde se
# lanzó uvicorn — el CSV es evidencia, tiene que caer siempre en el mismo sitio.
_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MedidorLatencia:
    """Acumula muestras por iteración y resume el cumplimiento del indicador.

    Las muestras las escribe el hilo del tracker; el resumen puede leerse desde
    otro hilo (una ruta HTTP), de ahí el lock. Ningún método debe propagar una
    excepción al pipeline: medir nunca puede tumbar la clasificación.
    """

    def __init__(self, maxlen: int = 2000) -> None:
        self._muestras: deque[dict[str, float]] = deque(maxlen=maxlen)
        self._lock = threading.Lock()
        self._n_total: int = 0          # no se reduce aunque el deque descarte
        self._ultimo_corte: int = 0     # n_total del último reporte automático
        self._exportadas: int = 0       # filas ya volcadas al CSV de esta corrida
        self._ruta_csv: str | None = None

    # ── Captura de muestras ───────────────────────────────────────────────

    def registrar(self, etapas: dict[str, float]) -> None:
        """Agrega una iteración. `etapas` trae los tramos en milisegundos."""
        # max(1, ...): con 0 el corte se cumpliría en cada frame y volcaría el
        # CSV 30 veces por segundo.
        corte = max(1, Config.ML_LATENCIA_ITERACIONES)
        with self._lock:
            self._muestras.append(etapas)
            self._n_total += 1
            listo = self._n_total - self._ultimo_corte >= corte
            if listo:
                self._ultimo_corte = self._n_total
        if listo:
            self.reportar()

    # ── Resumen ───────────────────────────────────────────────────────────

    def resumen(self) -> dict:
        """Estadísticos por tramo y veredicto contra el objetivo de la tesis."""
        with self._lock:
            muestras = list(self._muestras)
            n_total = self._n_total

        if not muestras:
            return {"n": 0, "n_total": 0, "cumple": False, "tramos": {}}

        objetivo = Config.ML_LATENCIA_OBJETIVO_MS
        exigidas = max(1, Config.ML_LATENCIA_ITERACIONES)
        # El indicador pide iteraciones CONSECUTIVAS, así que la racha se calcula
        # en orden cronológico. Ordenar aquí perdería justo lo que se mide: un
        # pico aislado en el warmup no debe invalidar 700 iteraciones limpias.
        racha = racha_max = 0
        dentro = 0
        for m in muestras:
            if m["total_ms"] <= objetivo:
                dentro += 1
                racha += 1
                racha_max = max(racha_max, racha)
            else:
                racha = 0

        return {
            "n": len(muestras),
            "n_total": n_total,
            "objetivo_ms": objetivo,
            "iteraciones_exigidas": exigidas,
            "dentro_objetivo": dentro,
            "pct_dentro": round(100.0 * dentro / len(muestras), 2),
            "racha_max": racha_max,
            "cumple": racha_max >= exigidas,
            "tramos": {t: self._estadisticos([m[t] for m in muestras]) for t in TRAMOS},
        }

    @staticmethod
    def _estadisticos(valores: list[float]) -> dict[str, float]:
        ordenados = sorted(valores)
        return {
            "min": round(ordenados[0], 2),
            "media": round(statistics.fmean(ordenados), 2),
            "p50": round(_percentil(ordenados, 50), 2),
            "p95": round(_percentil(ordenados, 95), 2),
            "max": round(ordenados[-1], 2),
        }

    # ── Evidencia en disco ────────────────────────────────────────────────

    def exportar_csv(self) -> str | None:
        """Anexa al CSV de esta corrida las iteraciones aún no escritas.

        Incremental a propósito: reescribir el archivo completo en cada corte
        significaba decenas de MB y decenas de archivos por minuto, y el costo
        del volcado caía dentro del hilo del tracker — el CSV certificaría un
        pipeline fluido mientras el real se frena cada N iteraciones.

        Retorna la ruta del CSV, o None si no hay nada que escribir o si falló
        la escritura (nunca lanza: medir no puede tumbar la clasificación).
        """
        with self._lock:
            pendientes = self._n_total - self._exportadas
            if pendientes <= 0:
                return self._ruta_csv
            # Si el deque descartó muestras viejas solo se puede volcar lo que queda.
            pendientes = min(pendientes, len(self._muestras))
            nuevas = list(self._muestras)[-pendientes:]
            primera = self._n_total - pendientes + 1
            if self._ruta_csv is None:
                base = Config.ML_LATENCIA_DIR
                if not os.path.isabs(base):
                    base = os.path.join(_RAIZ, base)
                marca = time.strftime("%Y%m%d_%H%M%S")
                self._ruta_csv = os.path.join(base, f"latencia_{marca}.csv")
            ruta = self._ruta_csv
            self._exportadas = self._n_total

        try:
            os.makedirs(os.path.dirname(ruta), exist_ok=True)
            escribir_cabecera = not os.path.exists(ruta)
            with open(ruta, "a", newline="", encoding="utf-8") as fh:
                escritor = csv.writer(fh)
                if escribir_cabecera:
                    escritor.writerow(("iteracion",) + TRAMOS)
                for i, m in enumerate(nuevas, start=primera):
                    escritor.writerow([i] + [round(m[t], 3) for t in TRAMOS])
            return ruta
        except OSError as exc:
            print(f"[latencia] No se pudo escribir el CSV ({exc}) - la medicion continua")
            return None

    def reportar(self) -> dict:
        """Imprime el bloque para la bitácora y anexa el CSV. Retorna el resumen."""
        r = self.resumen()
        if not r["n"]:
            return r

        veredicto = "CUMPLE" if r["cumple"] else "NO CUMPLE"
        print("\n" + "=" * 70)
        print(f"LATENCIA DEL PIPELINE - {r['n']} iteraciones (acumuladas: {r['n_total']})")
        print(f"Objetivo: total <= {r['objetivo_ms']:.0f} ms en >= {r['iteraciones_exigidas']} "
              f"iteraciones consecutivas")
        print("-" * 70)
        print(f"{'tramo':<18}{'min':>9}{'media':>9}{'p50':>9}{'p95':>9}{'max':>9}")
        for tramo in TRAMOS:
            e = r["tramos"][tramo]
            print(f"{tramo:<18}{e['min']:>9.2f}{e['media']:>9.2f}"
                  f"{e['p50']:>9.2f}{e['p95']:>9.2f}{e['max']:>9.2f}")
        print("-" * 70)
        print(f"Dentro del objetivo : {r['dentro_objetivo']}/{r['n']} ({r['pct_dentro']}%)")
        print(f"Racha consecutiva   : {r['racha_max']} (se exigen {r['iteraciones_exigidas']})")
        print(f"VEREDICTO: {veredicto}")
        print("Latencia de DECISION (captura -> registro). No incluye SERVO_DELAY_S,")
        print("espera programada del viaje camara -> servo, que no es computo.")
        ruta = self.exportar_csv()
        if ruta:
            print(f"CSV: {ruta}")
        print("=" * 70 + "\n")
        return r

    def resetear(self) -> None:
        """Cierra la corrida actual y descarta las muestras (nuevo lote).

        Exporta antes de limpiar: si no, las iteraciones posteriores al último
        corte se perderían como evidencia. La corrida siguiente abre su propio CSV.
        """
        self.exportar_csv()
        with self._lock:
            self._muestras.clear()
            self._n_total = 0
            self._ultimo_corte = 0
            self._exportadas = 0
            self._ruta_csv = None


def _percentil(ordenados: list[float], p: float) -> float:
    """Percentil por interpolación lineal (misma convención que numpy.percentile).
    `ordenados` ya viene ordenado."""
    if len(ordenados) == 1:
        return ordenados[0]
    pos = (len(ordenados) - 1) * p / 100.0
    bajo = int(pos)
    alto = min(bajo + 1, len(ordenados) - 1)
    return ordenados[bajo] + (ordenados[alto] - ordenados[bajo]) * (pos - bajo)


medidor_latencia = MedidorLatencia()
