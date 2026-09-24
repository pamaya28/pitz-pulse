# Pitz Pulse

Triage inteligente de solicitudes internas: recibe mensajes en español/portugués (como los que hoy llegan por Slack a Product & Tech) y los clasifica automáticamente por categoría, prioridad, área sugerida e idioma, usando un modelo de lenguaje.

## Stack elegido y por qué

**Python + Flask + SQLite.**

Elegí Python porque es el lenguaje con el que tengo más práctica, y Flask porque es lo más simple posible para exponer dos endpoints sin necesitar un framework grande encaja con el pedido del case de preferir "una solución simple que funcione" antes que algo ambicioso a medio terminar. SQLite porque no necesito nada más que guardar unas cuantas filas localmente, sin levantar infraestructura aparte.

Para la clasificación uso la API de Anthropic (Claude), con `temperature=0` para resultados reproducibles, y un **modo mock** que clasifica con reglas de palabras clave cuando no hay API key configurada así el proyecto corre completo sin costo y sin depender de ninguna key para poder probarlo.

## Cómo instalar y correr

```bash
cd pitz-pulse

python -m venv venv
source venv/bin/activate      # en Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Por defecto USE_MOCK=true, así que el proyecto ya funciona sin tocar nada más.
# Para usar Claude de verdad: poner USE_MOCK=false y pegar tu ANTHROPIC_API_KEY en .env

python process_anexo.py   # genera resultados.json
python app.py              # levanta la API en http://localhost:5000
```

## Endpoints

**POST /solicitudes** — clasifica y guarda un mensaje nuevo

En Mac/Linux:
```bash
curl -X POST http://localhost:5000/solicitudes \
  -H "Content-Type: application/json" \
  -d '{"id": "MSG-99", "mensaje": "No puedo acceder al panel, me sale error 500"}'
```

**En Windows** 
```PowerShell
curl.exe -X POST "http://127.0.0.1:5000/solicitudes" `
  -H "Content-Type: application/json" `
  -d '{"id":"MSG-99","mensaje":"No puedo acceder al panel, me sale error 500"}'


Invoke-WebRequest -Uri "http://127.0.0.1:5000/solicitudes" `
  -Method POST -ContentType "application/json" `
  -Body '{"id":"MSG-99","mensaje":"No puedo acceder al panel, me sale error 500"}'

curl.exe -X POST "http://127.0.0.1:5000/solicitudes" `
  -H "Content-Type: application/json" `
  -d '{"mensaje":"Falta el id"}'


```

El escapado de comillas de `curl` si llega a dar problemas porque se pega directo; es más confiable guardar el JSON en una variable primero:
```powershell
$body = '{"id": "MSG-99", "mensaje": "No puedo acceder al panel, me sale error 500"}'
curl.exe -X POST "http://127.0.0.1:5000/solicitudes" -H "Content-Type: application/json" -d $body
```

**GET /solicitudes** — lista lo guardado, con filtros opcionales

```PowerShell
curl http://localhost:5000/solicitudes  -solicitudes guardadas en la base de datos
curl http://localhost:5000/solicitudes?categoria=bug   -lista solicitudes de categoria especificar 
curl "http://localhost:5000/solicitudes?categoria=bug&prioridad=alta"  -Lista solo las solicitudes según su nivel de urgencia (alta, media, baja)
curl.exe -i -X DELETE "http://127.0.0.1:5000/solicitudes" -Método incorrecto sobre la misma ruta
```

**GET /health** — chequeo rápido de que el servicio está arriba y en qué modo corre

## Manejo de errores y validación

- Si el modelo devuelve un JSON con campos fuera de los valores permitidos, `validar_resultado()` lo detecta y se reintenta la petición (hasta 3 veces, con una pequeña espera creciente entre intentos).
- Si el modelo envuelve la respuesta en \`\`\`json ... \`\`\`, el código lo limpia antes de intentar parsear el JSON.
- Si después de los reintentos sigue sin poder clasificar, `POST /solicitudes` responde con un error 502 en vez de romperse.


## Qué quedó pendiente

No implementé los extras opcionales (vista web, integración con Slack, Docker, detección de duplicados, tests automatizados) para priorizar que la parte obligatoria estuviera simple, completa y bien explicada, como sugiere el enunciado.

## Sobre el uso de IA
https://claude.ai/share/96d8bcf9-489f-43ff-8c3e-1299f060766b

