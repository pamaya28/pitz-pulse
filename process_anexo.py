import json
import os
from pathlib import Path

from dotenv import load_dotenv

import classifier
import db

load_dotenv()

USE_MOCK = os.getenv("USE_MOCK", "true").strip().lower() == "true"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()

BASE_DIR = Path(__file__).parent


def main():
    with open(BASE_DIR / "mensajes.json", encoding="utf-8") as f:
        mensajes = json.load(f)

    cliente = None
    if not USE_MOCK and ANTHROPIC_API_KEY:
        import anthropic

        cliente = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    db.init_db()

    resultados = []
    for m in mensajes:
        clasificacion = classifier.clasificar_mensaje(
            m["id"], m["mensaje"], use_mock=USE_MOCK, cliente=cliente
        )
        db.guardar_solicitud(clasificacion, mensaje_original=m["mensaje"])
        resultados.append(clasificacion)
        print(f"{m['id']} -> categoria={clasificacion['categoria']} prioridad={clasificacion['prioridad']}")

    with open(BASE_DIR / "resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    modo = "mock" if (USE_MOCK or cliente is None) else "claude"
    print(f"\nListo. {len(resultados)} mensajes clasificados en modo '{modo}'. Ver resultados.json")


if __name__ == "__main__":
    main()