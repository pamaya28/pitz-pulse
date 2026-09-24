# Registro de uso de IA

Usé Claude durante todo el desarrollo de este case, ya que estoy empezando en programación de integraciones y el enunciado explícitamente invita a usar asistentes de código. Estos son ejemplos concretos de cómo lo usé:

**1. Diseño del prompt de clasificación**
Le pedí a Claude que me ayudara a redactar el prompt de sistema, dándole el contexto completo del problema. Revise la información inicial brindada y continue con la redacción del criterio de prioridad para que coincidiera literalmente con el que pide el enunciado.

**2. Manejo de errores y reintentos**
No sabía cómo estructurar el classifier.py le pedi que explicara la logica y verificara lo que ya llevaba de codigo, asimismo le pedi apoyo en la estructura de reintentos con backoff en Python. Le pedí que me explicara la lógica en simple antes de mostrarme el código, y luego que me ayudara a implementarla. Le pedí que me explicara línea por línea qué hacía la limpieza del JSON, porque no entendía por qué era necesaria — me explicó que a veces el modelo envuelve el JSON en markdown aunque se le pida que no lo haga.

**3. Modo mock sin API key**
Le expliqué que no tenía acceso a una API key paga, y le pedí una alternativa que permitiera correr y probar todo el proyecto igual. Propuso un clasificador simple basado en palabras clave. Al correrlo sobre los 12 mensajes, noté que el mensaje del CNPJ mal (MSG-08) se estaba clasificando como "otro" en vez de "bug", así que ajustamos juntas la lista de palabras clave.

**4. Explicación de conceptos para poder defenderlos**
Como no tengo experiencia previa con Flask, le pedí que me explicara sin tecnicismos qué hace cada parte del código antes de aceptarlo: qué es un endpoint POST vs GET, y qué significa "validar" la respuesta del modelo.

**5. Estructuración de archivos y commits**
Le pedí a la IA que me ayudara a definir la estructura inicial del proyecto en archivos separados (db.py, app.py, process_anexo.py), describiendo únicamente las responsabilidades de cada uno. La IA me devolvió versiones funcionales y luego le fui indicando ajustes incrementales (por ejemplo, simplificar funciones auxiliares, usar rutas relativas con Path(__file__).parent, y pasar explícitamente parámetros como use_mock y cliente). Esto me permitió llegar a un resultado alineado con lo que buscaba, manteniendo control sobre el diseño y entendiendo cada parte antes de aceptarla. 

**6. Depuración de las pruebas con curl en Windows**
Al probar los endpoints con `curl` en PowerShell, los comandos con comillas escapadas se rompían y devolvían errores confusos ("Could not resolve host"). Le describí el error tal cual aparecía en la terminal, y Claude identificó que era un problema de cómo PowerShell interpreta las comillas al pegar comandos largos, no un error del código en sí. Propuso guardar el JSON en una variable (`$body = '...'`) antes de pasarlo a `curl.exe`, lo cual probé y sí funcionó — confirmé con un `GET` posterior que el registro quedó guardado correctamente.

**Lo que no acepté sin revisar:** en todos los casos, antes de aceptar código o texto, le pedí que me explicara la lógica en simple primero. Si algo no me quedaba claro, seguíamos ajustando hasta que sí pudiera repetirlo con mis palabras.