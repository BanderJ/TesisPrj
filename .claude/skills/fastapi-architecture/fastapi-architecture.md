---
id: fastapi-architecture
name: fastapi-architecture
description: Reglas de Clean Architecture, capas y psycopg2 para TESISPRJ.
---

# MISIÓN PRINCIPAL
Mantener separación de capas en TESISPRJ con código limpio, directo y sin duplicación funcional.

# 🎯 PRINCIPIOS CORE (No negociables)

## 1. ARQUITECTURA EN CAPAS (Separación estricta)
* **📂 src/models/** → SQL puro, persistencia, sin lógica.
* **📂 src/services/** → Lógica de negocio, orquestación.
* **📂 src/schemas/** → Validación Pydantic + Type Hints.
* **📂 src/routes/** → HTTP, flujo, sin lógica de negocio.
* **📂 src/database/** → Conexiones (psycopg2), try...finally siempre.
* **📂 src/apis/** → Clientes de APIs externas (Reniec, Factiliza, etc.), sin lógica de negocio. Solo se llaman desde services.

## 2. REGLA DE ORO: ANTES DE CREAR, PREGUNTAR
**SEMPRE** antes de proponer un método nuevo evalúa lo siguiente:
* ¿Ya existe una función que haga esto en otra capa? → **REUTILIZAR**.
* ¿Es lógica duplicada con pequeñas variaciones? → **PARAMETRIZAR** (1 método flexible).
* ¿Suma valor real o es "just in case code"? → Si no, **ELIMINAR**.

```python
# ❌ MAL: Métodos duplicados con variaciones menores
def obtener_usuario_activo(user_id):
    return db.obtener_uno("SELECT * FROM usuarios WHERE id=%s AND activo=true", [user_id])

def obtener_usuario_activo_con_rol(user_id, rol):
    return db.obtener_uno("SELECT * FROM usuarios WHERE id=%s AND activo=true AND rol=%s", [user_id, rol])

def obtener_usuario_por_email(email):
    return db.obtener_uno("SELECT * FROM usuarios WHERE email=%s", [email])

# ✅ BIEN: Un método flexible + parametrización
def obtener_usuario(user_id: int | None = None, email: str | None = None, filtros_extra: dict[str, any] | None = None) -> dict | None:
    """Método único y flexible. Parametrizable según necesidad."""
    query = "SELECT * FROM usuarios WHERE 1=1"
    params = []
    if user_id:
        query += " AND id=%s"
        params.append(user_id)
    elif email:
        query += " AND email=%s"
        params.append(email)
    
    if filtros_extra:
        for key, value in filtros_extra.items():
            query += f" AND {key}=%s"
            params.append(value)
    return db.obtener_uno(query, params)
```

---

# 📐 REGLAS DE PRAGMATISMO

### Simplicidad = Fuerza
* Si se resuelve en 5 líneas claras, no uses 20.
* Dict/List/Tuple para datos temporales (no siempre necesitas una clase).
* Comprensiones de lista/diccionario sin exceso.

### Type Hints (Obligatorio Python 3.10+)
```python
def procesar_datos(usuarios: list[dict], factor: float) -> dict[str, float]:
    return {u['id']: u['score'] * factor for u in usuarios}
```

### SQL Seguro (SIEMPRE parametrizado)
```python
# ❌ MAL
query = f"SELECT * FROM usuarios WHERE id={user_id}"

# ✅ BIEN
query = "SELECT * FROM usuarios WHERE id=%s"
db.obtener_uno(query, [user_id])
```

---

# 🏗️ ESTRUCTURA DE RESPUESTA
Propongo siempre en este orden:
1. **📂 Schema** (Pydantic)
2. **📂 Model** (SQL/Persistencia) o **📂 Api** (cliente externo)
3. **📂 Service** (Lógica, orquestación)
4. **📂 Route** (HTTP, flujo)

*Incluye SOLO lo necesario. Nada más.*

---

# 🚨 ANTI-PATRONES A DETECTAR Y REPORTAR
Si ves en el código:
* ✋ **Métodos que hacen casi lo mismo** → Fusionar en uno parametrizado.
* ✋ **Lógica de negocio en routes** → Mover a services.
* ✋ **Consultas SQL en services** → Mover a models.
* ✋ **Llamadas a APIs externas en routes** → Mover a services (que llaman a apis/).
* ✋ **Lógica de negocio en apis/** → Mover a services. apis/ solo hace HTTP.
* ✋ **Validación fuera de schemas** → Mover a Pydantic.
* ✋ **try...finally sin db.close()** → Rechazar y corregir.
* ✋ **Métodos sin type hints** → Exigir claridad.
* ✋ **API retorna datos crudos que obligan al frontend a tomar decisiones de negocio** → El service debe calcular y devolver valores derivados listos para mostrar.

---

# 📡 REGLA: CONTRATOS DE API RICOS (Frontend nunca decide reglas de negocio)

El frontend es capa de presentación. **Nunca** debe contener listas de nombres de clases, umbrales, pesos ni ninguna regla que viva en el backend.

**Señales de alarma en el frontend — si ves esto, el endpoint está mal diseñado:**
```javascript
// ❌ MAL: el frontend conoce los nombres de las clases del modelo ML
const CLASES_SANAS = new Set(['verde', 'sano', 'bueno']);
const totalDefectos = Object.entries(conteo)
    .filter(([cls]) => !CLASES_SANAS.has(cls))
    .reduce((sum, [, v]) => sum + v, 0);

// ❌ MAL: el frontend suma clases específicas del modelo
const negro = (conteo['negro'] || 0) + (conteo['defecto'] || 0);

// ❌ MAL: el frontend aplica umbrales de negocio
const esEspecialty = totalDefectos <= 15;
```

**El service debe calcular y exponer valores listos:**
```python
# ✅ BIEN: service calcula total_defectos y total_sanos usando EQUIVALENCIAS
def obtener_conteo_enriquecido(self) -> dict:
    conteo = self.obtener_conteo_actual()
    eq = self.tracker.EQUIVALENCIAS_DEFECTO
    total_defectos = sum(v for k, v in conteo.items() if eq.get(k, 0.0) > 0.0)
    total_sanos    = sum(v for k, v in conteo.items() if eq.get(k, 0.0) == 0.0)
    return {
        "conteo":           conteo,
        "total_granos":     total_defectos + total_sanos,
        "total_defectos":   total_defectos,
        "total_sanos":      total_sanos,
        "clases_detectadas": len(conteo),
    }
```

```javascript
// ✅ BIEN: frontend solo muestra
const data = await fetch('/video/lote/conteo').then(r => r.json());
totalDefectsEl.textContent = data.total_defectos;
totalSanosEl.textContent   = data.total_sanos;
```

**Regla práctica:** Si cambiar el nombre de una clase del modelo ML requiere tocar un template HTML → el contrato de API está mal diseñado. Corrígelo en el service.

---

# 💡 CÓMO PENSAR
**Preguntarte ante cada propuesta:**


| Pregunta | Acción |
| :--- | :--- |
| ¿Esto ya existe? | Reutilizar |
| ¿Es una variación menor? | Parametrizar 1 método |
| ¿Añade valor único? | Crear (si es sí) |
| ¿El código es auto-explicativo? | Sí → Bueno |
| ¿Necesito un docstring? | Sí → Código no es claro |

---

# 📋 CHECKLIST ANTES DE PROPONER CÓDIGO
- [ ] ¿Existe algo similar en otra capa?
- [ ] ¿Puedo parametrizar en lugar de duplicar?
- [ ] ¿Tiene type hints?
- [ ] ¿Las consultas SQL están parametrizadas?
- [ ] ¿El código se explica solo? (sin docstrings innecesarios)
- [ ] ¿try...finally con db.close()? (si toca BD)
- [ ] ¿Respeta la capa arquitectónica asignada?
- [ ] ¿Eliminar código muerto o "just in case"?

---

# 🗄️ INFRAESTRUCTURA: psycopg2 + Clase Connection
```python
# src/database/bd.py (referencia)
class Connection:
    autocommit = False
    def obtener(query, params): # Múltiples filas
    def obtener_uno(query, params): # Una fila
    def ejecutar(query, params): # Inserción/Actualización
    def commit(): # Confirmar cambios
    def rollback(): # Deshacer cambios
    def close(): # Cerrar conexión (SIEMPRE en finally)
```

**Patrón obligatorio:**
```python
db = Connection()
try:
    resultado = db.obtener_uno("SELECT...", params)
finally:
    db.close()
```

---

# 🎓 EJEMPLOS DE OPTIMIZACIÓN

### CASO 1: Métodos Duplicados
```python
# ❌ ANTES (3 métodos, 1 lógica)
def crear_usuario_admin(data): ...
def crear_usuario_cliente(data): ...
def crear_usuario_moderador(data): ...

# ✅ DESPUÉS (1 método, flexible)
def crear_usuario(data: UsuarioSchema, rol: str = "cliente") -> dict:
    return db.ejecutar("INSERT INTO usuarios (email, rol, ...) VALUES (%s, %s, ...)", [...])
```

### CASO 2: Lógica en Capa Equivocada
```python
# ❌ ANTES (lógica en route)
@app.post("/usuarios")
def crear_usuario(data):
    if data.edad < 18:
        return {"error": "..."}
    # Inserción directa...

# ✅ DESPUÉS (separación clara)
# schemas/usuario.py
class UsuarioSchema(BaseModel):
    edad: int = Field(gt=17)
    email: EmailStr

# services/usuario_service.py
def crear_usuario(data: UsuarioSchema) -> dict:
    usuario = UsuarioModel.crear(data)
    return usuario

# routes/usuario_routes.py
@app.post("/usuarios")
def crear(data: UsuarioSchema):
    return UsuarioService.crear_usuario(data)
```

---

# 🔄 MINDSET FINAL
**Menos, pero mejor.** No es cuánto código escribas, sino cuán eficientemente resuelves el problema. Si duplicas funcionalidad, algo está mal en el diseño.

**Cada línea debe:**
* Tener un propósito claro.
* Estar en la capa correcta.
* No existir en otra forma.
