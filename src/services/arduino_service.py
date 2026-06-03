from src.config import Config
from src.utilities.arduino_serial import arduino_serial


class ArduinoService:
    def obtener_estado(self) -> dict:
        estado = arduino_serial.obtener_estado()

        if not estado.conectado:
            return {
                "listo": False,
                "distancia": None,
                "conectado": False,
                "mensaje": f"Arduino no conectado ({Config.ARDUINO_PORT}). Verifique el cable USB.",
            }

        if estado.error and estado.distancia is None:
            return {
                "listo": False,
                "distancia": None,
                "conectado": True,
                "mensaje": "No se recibió lectura del sensor. Verifique el Arduino.",
            }

        dist = estado.distancia
        dist_str = f"{dist:.1f} cm" if dist is not None and dist >= 0 else "sin lectura"

        if estado.listo:
            return {
                "listo": True,
                "distancia": dist,
                "conectado": True,
                "mensaje": f"Muestra detectada a {dist_str}. Lista para iniciar.",
            }

        return {
            "listo": False,
            "distancia": dist,
            "conectado": True,
            "mensaje": "Debe cerrar la tapa luego de haber ingresado los granos de café para continuar al monitoreo.",
        }

    def obtener_peso(self) -> dict:
        estado = arduino_serial.obtener_estado()
        if not estado.conectado:
            return {
                "peso": None,
                "conectado": False,
                "mensaje": f"Arduino no conectado ({Config.ARDUINO_PORT}).",
            }

        peso = arduino_serial.obtener_peso()
        if peso is None:
            return {
                "peso": None,
                "conectado": True,
                "mensaje": "Esperando lectura de la báscula...",
            }

        peso_r = round(peso, 2)
        return {
            "peso": peso_r,
            "conectado": True,
            "mensaje": f"{peso_r} g",
        }

    def tarar_bascula(self) -> dict:
        ok = arduino_serial.enviar_comando("TARE")
        return {
            "ok": ok,
            "mensaje": "Tara enviada. La báscula se está calibrando." if ok else "No se pudo enviar tara. Verifique la conexión Arduino.",
        }

    def iniciar_motor(self) -> dict:
        ok = arduino_serial.enviar_comando("ON")
        return {
            "activo": ok,
            "mensaje": "Faja iniciada." if ok else "No se pudo iniciar la faja. Verifique la conexión Arduino.",
        }

    def detener_motor(self) -> dict:
        ok = arduino_serial.enviar_comando("OFF")
        return {
            "activo": False,
            "mensaje": "Faja detenida." if ok else "No se pudo detener la faja. Verifique la conexión Arduino.",
        }


arduino_service = ArduinoService()
