# Tabla de Defectos SCA — Referencia Rápida

> **Vigencia (30-sep-2026):** esta tabla se escribió para el modelo de 17 clases, que no llegó a
> producción. El modelo actual es binario y aplica las equivalencias de
> `src/ml/models/yolov26n_2cls/constants.py`: `defecto` = 1, `verde` = 0, `desconocido`
> (materia extraña) = 1.0. La validación de ambas tablas con Line Coffee Marañón sigue pendiente
> (INC-17). Ver [guia/02-modulo-ml.md](guia/02-modulo-ml.md).

## Solo 3 Grados en la Norma SCA

| Grado | Defectos Máximo | Specialty |
|-------|:---------------:|:---------:|
| **Grado 1** | 0–15 | ✅ Sí |
| **Grado 2** | 16–23 | ❌ No |
| **Grado 3** | 24–30 | ❌ No |
| **>30** | — | ❌ No clasificable |

---

## Equivalencias de Defectos (Muestra 350g)

### Categoría 1 — GRAVES (1 grano = 1 defecto)
```
- Grano negro
- Grano agrio
- Cereza seca
- Daño por hongos
- Broca grave (≥3 perforaciones)
```

### Categoría 2a — LEVES (3 granos = 1 defecto)
```
- Grano negro parcial
- Grano agrio parcial
```

### Categoría 2b — LEVES (5 granos = 1 defecto)
```
- Pergamino
- Flotador
- Inmaduro
- Averanado
- Concha
- Partido/Mordido/Cortado
- Cascarilla (cereza seca + pergamino)
```

### Categoría 2c — MÍNIMOS (10 granos = 1 defecto)
```
- Broca ligera (≤2 perforaciones)
```

---

## Ejemplo de Cálculo

**Lote analizado:** 100 granos

| Defecto | Granos | Equivalencia | Defectos |
|---------|:------:|:----------:|:--------:|
| Negro | 5 | 1 grano = 1 defecto | 5.0 |
| Inmaduro | 25 | 5 granos = 1 defecto | 5.0 |
| Broca ligera | 30 | 10 granos = 1 defecto | 3.0 |
| **TOTAL** | — | — | **13.0** |

**Resultado:** Grado 1 (Specialty) ✅

---

## ⚠️ Notas Críticas

1. **Materia extraña** (piedras, palos, vidrio): 1 objeto = 1 defecto (no por granos)
2. **Verde/Blanco/Deforme**: En SCA NO son defectos, son malformaciones. Si el modelo YOLO los detecta, verificar clasificación.
3. **Especialidad requiere ADEMÁS:**
   - Máximo 1 defecto categoría 1
   - Máximo 5 defectos categoría 2
   - Humedad 10–12%
   - Aw < 0.70
   - 0 quakers (al tostar)

4. **Verificación obligatoria:** Antes de deploy, revisar tabla oficial de **Line Coffee Marañón** — las equivalencias pueden variar.

