# Decisiones y reflexión

### ¿Cómo diseñé el prompt y por qué? ¿Qué contexto le di al modelo?

Le di al modelo tres cosas en el prompt de sistema: (1) la definición exacta de cada campo y sus valores permitidos, incluyendo el criterio de prioridad tal como lo especifica el enunciado, para no dejarlo a interpretación libre; (2) una instrucción explícita de responder solo con JSON, sin texto adicional. Usé `temperature=0` para que la clasificación sea lo más consistente posible entre corridas.

### ¿En qué mensajes crees que tu clasificador se equivoca o duda, y por qué?

Los más confusos son los que mezclan dos posibles categorías o donde la prioridad depende de contexto que no está en el mensaje por ser muy corto o ambiguo. Por ejemplo, MSG-05 ("no me aparecen los registros de la última campaña en HubSpot, no sé si es un problema de ustedes o nuestro") podría clasificarse como "bug" o como "consulta". MSG-09 ("la plataforma está lenta") es el caso más difícil: no dice qué tan lenta, para quién, ni desde cuándo, así que la prioridad real depende de información que simplemente no está — ahí es donde `requiere_info: true` debería activarse con más fuerza.

### ¿Cómo medirías si el clasificador funciona bien una vez en producción?

Empezaría con una muestra etiquetada a mano por alguien del equipo (50-100 mensajes reales) y mediría qué tan seguido la categoría, prioridad y área coinciden con lo que una persona hubiera puesto. Asimismo, mediría cuántas veces alguien tiene que "recategorizar" manualmente una solicitud después de que el sistema la clasificó, y si los mensajes marcados como `prioridad: alta` de verdad terminan atendiéndose rápido.

### Estimación aproximada de costo por mensaje y por mes (500 solicitudes/mes)

Usando Claude Sonnet a aproximadamente $3 por millón de tokens de entrada y $15 por millón de tokens de salida: el prompt de sistema son unos 400 tokens, un mensaje típico ronda los 100-150 tokens, y la respuesta JSON son unos 100 tokens (≈550 tokens de entrada y 100 de salida por mensaje):

- **Costo aproximado por mensaje: ~$0.003**
- **Costo aproximado por mes (500 mensajes): ~$1.50**

### Los mensajes pueden incluir datos fiscales (CNPJ) o de pagos. ¿Qué consideraciones tendrías?

No enviaría el mensaje completo sin revisar qué contiene si se puede evitar. Idealmente, antes de mandarlo a la API de terceros, correría una limpieza simple para enmascarar patrones que parezcan CNPJ o números de tarjeta. También revisaría la política de retención de datos del proveedor de IA (si guarda los prompts, por cuánto tiempo, si se usan para entrenar modelos). Dado que Pitz opera en Brasil y México, consideraría también qué dice la LGPD (Brasil) y la ley de protección de datos personales de México sobre enviar información personal o fiscal a un procesador externo.

### Si tuvieras dos semanas más, ¿qué construirías después?

Primero, una vista web simple para que el equipo de Product pueda ver y filtrar las solicitudes sin llamar a la API directamente. Segundo, la integración real con el webhook de Slack, para que recibir los mensajes sea automático desde el mensaje original. Tercero, detección de duplicados o mensajes muy similares (varios mensajes de prueba mencionan casos repetidos).