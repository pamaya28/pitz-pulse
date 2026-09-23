"""
Pitz Pulse — API HTTP.
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

import classifier
import db

load_dotenv()

USE_MOCK = os.getenv("USE_MOCK", "true").strip().lower() == "true"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()

app = Flask(__name__)
db.init_db()

_cliente_anthropic = None
if not USE_MOCK and ANTHROPIC_API_KEY:
    import anthropic
    _cliente_anthropic = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "modo": "mock" if USE_MOCK else "claude"}), 200

@app.route("/solicitudes", methods=["POST"])
def crear_solicitud():
    body = request.get_json(force=True, silent=True)

    if not body or "id" not in body or "mensaje" not in body:
        return jsonify({"error": "El body debe incluir 'id' y 'mensaje'"}), 400

    try:
        clasificacion = classifier.clasificar_mensaje(
            body["id"], body["mensaje"], use_mock=USE_MOCK, cliente=_cliente_anthropic
        )
    except Exception as e:
        return jsonify({"error": f"No se pudo clasificar el mensaje: {e}"}), 502

    db.guardar_solicitud(clasificacion, mensaje_original=body["mensaje"])
    return jsonify(clasificacion), 201

@app.route("/solicitudes", methods=["GET"])
def listar_solicitudes_endpoint():
    categoria = request.args.get("categoria")
    prioridad = request.args.get("prioridad")
    resultados = db.listar_solicitudes(categoria=categoria, prioridad=prioridad)
    return jsonify(resultados), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
