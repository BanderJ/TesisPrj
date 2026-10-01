"""PostToolUse hook: recuerda espejar src/config.py en src/config-example.py.

src/config.py está en .gitignore (credenciales propias). El archivo publicado es
src/config-example.py. Cada cambio estructural en config.py debe reflejarse en la
plantilla con los secretos reemplazados por placeholders.

Se dispara tras Write/Edit. Si el archivo tocado NO es src/config.py, no imprime
nada y sale 0. Si lo es, emite un systemMessage y additionalContext para Claude.
"""
import json
import sys


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    ruta = (data.get("tool_input", {}).get("file_path") or "").replace("\\", "/")
    if not ruta.endswith("src/config.py"):
        return 0

    print(json.dumps({
        "systemMessage": (
            "config.py editado: refleja el cambio estructural en "
            "src/config-example.py (misma clase Config, secretos como placeholder)."
        ),
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                "Acabas de editar src/config.py, que está en .gitignore. El archivo "
                "publicado en Git es src/config-example.py. Si tu cambio agregó, "
                "renombró o comentó un atributo de la clase Config, aplica el mismo "
                "cambio a src/config-example.py ahora, reemplazando cualquier valor "
                "sensible (PASSWORD, tokens) por un placeholder. Ambos archivos deben "
                "quedar con los mismos atributos de Config."
            ),
        },
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
