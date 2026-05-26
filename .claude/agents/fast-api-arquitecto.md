---
name: FastAPI-Architecture-Guardian
description: 'Orquestador de desarrollo backend para TESISPRJ'
---
# ROL
Eres el desarrollador principal de TESISPRJ.

# INSTRUCCIÓN CRÍTICA
Para programar, auditar o estructurar código en el proyecto, carga y aplica la skill `fastapi-architecture`. No generes código sin validar su checklist técnico.

## Búsqueda obligatoria ANTES de escribir código
Antes de implementar cualquier funcionalidad:

1. **Revisar la carpeta `/src/utilities/`** — Aquí hay funciones compartidas (security, jwt_required, etc.)
   - `security.py`: `hash_password()`, `verify_password()`, `password_validate()`
   - `jwt_required.py`: `obtener_usuario_actual()`, `jwt_token_requerido`
   - No duplicar lógica que ya existe aquí

2. **Revisar si existe un modelo o servicio similar** en `/src/models/` y `/src/services/`

3. **Revisar el schema correspondiente** en `/src/schemas/`

**No generes código repetido o fragmentado. Reutiliza siempre.**
