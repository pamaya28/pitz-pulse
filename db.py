"""
Persistencia liviana con SQLite para las solicitudes clasificadas.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "pitz_pulse.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS solicitudes (
            id TEXT PRIMARY KEY,
            categoria TEXT NOT NULL,
            prioridad TEXT NOT NULL,
            area_sugerida TEXT NOT NULL,
            idioma TEXT NOT NULL,
            resumen TEXT NOT NULL,
            requiere_info INTEGER NOT NULL,
            pregunta_seguimiento TEXT,
            mensaje_original TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def guardar_solicitud(clasificacion: dict, mensaje_original: str = ""):
    conn = get_connection()
    conn.execute(
        """
        INSERT OR REPLACE INTO solicitudes
        (id, categoria, prioridad, area_sugerida, idioma, resumen, requiere_info, pregunta_seguimiento, mensaje_original)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            clasificacion["id"],
            clasificacion["categoria"],
            clasificacion["prioridad"],
            clasificacion["area_sugerida"],
            clasificacion["idioma"],
            clasificacion["resumen"],
            int(clasificacion["requiere_info"]),
            clasificacion["pregunta_seguimiento"],
            mensaje_original,
        ),
    )
    conn.commit()
    conn.close()
def listar_solicitudes(categoria: str = None, prioridad: str = None) -> list:
    conn = get_connection()
    query = "SELECT * FROM solicitudes WHERE 1=1"
    params = []
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if prioridad:
        query += " AND prioridad = ?"
        params.append(prioridad)
    query += " ORDER BY rowid DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    resultado = []
    for r in rows:
        d = dict(r)
        d["requiere_info"] = bool(d["requiere_info"])
        resultado.append(d)
    return resultado