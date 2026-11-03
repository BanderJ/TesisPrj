# CLAUDE.md

Las instrucciones del proyecto son comunes para todas las IA y viven en `AGENTS.md`.
La línea siguiente las importa completas:

@AGENTS.md

## Solo para Claude Code

- **Auditoría obligatoria:** después de cambiar `src/routes`, `src/services`, `src/models`,
  `src/schemas`, `src/apis`, `src/ml`, `src/templates` o `src/static`, delega en el subagente
  `architecture-compliance-auditor` antes de dar el trabajo por terminado.
- **Skills:** `fastapi-architecture` (backend), `frontend-coffeeren` (plantillas, CSS, JS),
  `documentacion-informes` (documentación), `profesionalismo-sin-ia` (estilo de salida).
  Cárgalas cuando la tarea corresponda.
- **Hook:** al editar `src/config.py`, un hook recuerda replicar el cambio en
  `src/config-example.py` (`.claude/hooks/config_example_reminder.py`).
