# Instrucciones para GitHub Copilot

Las instrucciones del proyecto son comunes para todas las IA y viven en `AGENTS.md`, en la raíz
del repositorio. Léelo completo antes de hacer cualquier cambio.

Lo mínimo, por si no se carga:

- Responder en español, sin emojis, con tono técnico.
- No inventar umbrales ni reglas de negocio: preguntar antes.
- Respetar las cuatro capas: routes (HTTP), services (lógica), models (SQL parametrizado), schemas (validación).
- No modificar `servo_controller.py`, `arduino_serial.py`, `imgsz=640` ni los tiempos del servo.
- Todo cambio en `src/config.py` se replica en `src/config-example.py`.
- Contexto y estado del sistema: `docs/guia/README.md`.
