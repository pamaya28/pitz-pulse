import json
import time

CATEGORIAS = {"bug", "datos", "acceso", "automatizacion", "consulta", "otro"}
PRIORIDADES = {"alta", "media", "baja"}
AREAS = {"backend", "frontend", "data", "devops", "producto", "digital_transformation"}
IDIOMAS = {"es", "pt"}

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """Eres un asistente que clasifica mensajes internos que llegan por Slack en Pitz, un marketplace B2B y plataforma SaaS que conecta talleres mecánicos, vendedores de autopartes y distribuidores en Brasil y México. Los mensajes los escriben personas de distintas áreas (Comercial, Operaciones, Soporte, Finanzas, Marketing, People) pidiendo ayuda al equipo de Product & Tech.

Para cada mensaje debes devolver ÚNICAMENTE un objeto JSON válido (sin texto adicional, sin markdown, sin explicaciones antes o después) con exactamente estos campos:

- "id": el id del mensaje, tal como te lo doy.
- "categoria": uno de "bug", "datos", "acceso", "automatizacion", "consulta", "otro".
- "prioridad": uno de "alta", "media", "baja".
    - alta: afecta a clientes, dinero, obligaciones legales, o bloquea una operación.
    - media: afecta a un área interna o a pocos usuarios, y tiene alguna alternativa temporal.
    - baja: dudas, mejoras o pedidos sin impacto inmediato en clientes o dinero.   
- "area_sugerida": uno de "backend", "frontend", "data", "devops", "producto", "digital_transformation".
- "idioma": "es" o "pt", según el idioma en que está escrito el mensaje original.
- "resumen": máximo 20 palabras, en español, resumiendo claramente qué se pide o qué está pasando.
- "requiere_info": true o false. true si el mensaje no da suficiente información concreta para poder actuar.
- "pregunta_seguimiento": si "requiere_info" es true, la pregunta puntual que le harías a quien escribió el mensaje. Si "requiere_info" es false, este campo debe ser null.

Responde solo con el objeto JSON, nada más."""


def build_user_prompt(mensaje_id: str, texto: str) -> str:
    return (
        f'Mensaje id="{mensaje_id}":\n"""{texto}"""\n\n'
        "Clasifica este mensaje siguiendo exactamente las reglas indicadas en las instrucciones."
    )


def validar_resultado(data: dict, mensaje_id: str) -> list:
    """Revisa que la respuesta del modelo tenga el formato y los valores esperados."""
    errores = []

    if not isinstance(data, dict):
        return ["la respuesta no es un objeto JSON"]

    if data.get("id") != mensaje_id:
        errores.append(f"id no coincide (esperado {mensaje_id}, llegó {data.get('id')})")
    if data.get("categoria") not in CATEGORIAS:
        errores.append(f"categoria inválida: {data.get('categoria')!r}")
    if data.get("prioridad") not in PRIORIDADES:
        errores.append(f"prioridad inválida: {data.get('prioridad')!r}")
    if data.get("area_sugerida") not in AREAS:
        errores.append(f"area_sugerida inválida: {data.get('area_sugerida')!r}")
    if data.get("idioma") not in IDIOMAS:
        errores.append(f"idioma inválido: {data.get('idioma')!r}")
    if not isinstance(data.get("resumen"), str) or not data.get("resumen", "").strip():
        errores.append("resumen inválido o vacío")
    if not isinstance(data.get("requiere_info"), bool):
        errores.append("requiere_info debe ser true o false")
    if data.get("requiere_info") is True and not data.get("pregunta_seguimiento"):
        errores.append("falta pregunta_seguimiento cuando requiere_info es true")

    return errores


def _extraer_json(texto_crudo: str) -> dict:
    """El modelo a veces envuelve el JSON en ```json ... ``` aunque se le pida que no lo haga."""
    limpio = texto_crudo.strip()
    if limpio.startswith("```"):
        limpio = limpio.strip("`")
        if limpio.lower().startswith("json"):
            limpio = limpio[4:]
    return json.loads(limpio.strip())


def clasificar_con_claude(mensaje_id: str, texto: str, cliente, max_reintentos: int = 3) -> dict:
    """Clasifica un mensaje usando la API de Anthropic, con reintentos ante timeouts,
    respuestas inválidas o JSON mal formado."""
    ultimo_error = None

    for intento in range(1, max_reintentos + 1):
        try:
            respuesta = cliente.messages.create(
                model=MODEL,
                max_tokens=500,
                temperature=0,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": build_user_prompt(mensaje_id, texto)}],
            )
            contenido = respuesta.content[0].text
            data = _extraer_json(contenido)

            errores = validar_resultado(data, mensaje_id)
            if errores:
                raise ValueError(f"Respuesta fuera de formato: {errores}")

            if data.get("requiere_info") is False:
                data["pregunta_seguimiento"] = None

            return data

        except Exception as e:
            ultimo_error = e
            if intento < max_reintentos:
                time.sleep(intento)  # backoff simple: 1s, 2s...

    raise RuntimeError(
        f"No se pudo clasificar el mensaje {mensaje_id} tras {max_reintentos} intentos. "
        f"Último error: {ultimo_error}"
    )


def clasificar_mock(mensaje_id: str, texto: str) -> dict:
    """Clasificador simple basado en palabras clave. No necesita ninguna API key
    y sirve para correr y probar todo el proyecto sin costo (ver README)."""
    t = texto.lower()

    palabras_pt = [
        "não", "voce", "você", "preciso", "pra ", " oi ", "oi ", "pessoal",
        "estão", "está saindo", "falou", "reclamação", "algumas", "dá pra",
        "qual é", "perguntou", "soube",
    ]
    idioma = "pt" if any(p in t for p in palabras_pt) else "es"

    if any(p in t for p in ["error 500", "erro", "falla", "no funciona", "não funciona", "some no celular", "bug", "errado", "saindo com"]):
        categoria = "bug"
    elif any(p in t for p in ["acceso al panel", "acesso", "dar acceso", "permiso"]):
        categoria = "acceso"
    elif any(p in t for p in ["planilha", "planilla", "reporte", "cuántos", "quantos", "datos"]):
        categoria = "datos"
    elif any(p in t for p in ["automat", "copio manualmente", "dá pra automatizar", "mensaje a cada persona"]):
        categoria = "automatizacion"
    elif any(p in t for p in ["diferença", "diferencia", "cómo lo proceso", "cómo proceso", "duda"]):
        categoria = "consulta"
    else:
        categoria = "otro"

    if any(p in t for p in ["urgente", "reembolso", "cnpj errado", "error 500", "no puede subir", "pagó dos veces"]):
        prioridad = "alta"
    elif any(p in t for p in ["lenta", "some no celular", "acceso al panel", "planilha", "planilla", "hubspot"]):
        prioridad = "media"
    else:
        prioridad = "baja"

    if categoria == "bug":
        area = "backend"
    elif categoria == "acceso":
        area = "devops"
    elif categoria == "datos":
        area = "data"
    elif categoria == "automatizacion":
        area = "digital_transformation"
    else:
        area = "producto"

    poco_detalle = len(texto) < 70 and not any(p in t for p in ["cnpj", "guadalajara", "monterrey"])
    requiere_info = poco_detalle

    palabras = texto.split()
    resumen = " ".join(palabras[:20])
    if len(palabras) > 20:
        resumen += "..."

    return {
        "id": mensaje_id,
        "categoria": categoria,
        "prioridad": prioridad,
        "area_sugerida": area,
        "idioma": idioma,
        "resumen": resumen,
        "requiere_info": bool(requiere_info),
        "pregunta_seguimiento": (
            "¿Puedes darnos más detalles concretos (a quién le pasó, cuándo, y qué intentaste)?"
            if requiere_info else None
        ),
    }


def clasificar_mensaje(mensaje_id: str, texto: str, use_mock: bool = True, cliente=None) -> dict:
    """Punto de entrada único: decide si usar el modo mock o llamar a Claude de verdad."""
    if use_mock or cliente is None:
        return clasificar_mock(mensaje_id, texto)
    return clasificar_con_claude(mensaje_id, texto, cliente)