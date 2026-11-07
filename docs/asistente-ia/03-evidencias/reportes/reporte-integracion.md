# Reporte de validación técnica de integración y estabilidad de red

- **Fecha:** 07/11/2026
- **Componentes:** Vue 3 (Vite, puerto 5173) → Django REST (puerto 8000) → Ollama (puerto 11434)

## 1. Conectividad de red

| Prueba | Resultado | Evidencia |
|---|---|---|
| `ollama --version` | 0.40.15 ✅ | 04-ollama-version-modelos-red.png |
| `ollama list` muestra `sigta-ai` y `llama3.2:3b` | ✅ | 04-ollama-version-modelos-red.png |
| `OLLAMA_HOST=0.0.0.0:11434` configurado de forma persistente (variable de usuario) | ✅ | — |
| Regla de firewall de entrada, TCP 11434, perfil Privado | ✅ habilitada | 03-firewall-regla.png |
| `GET http://192.168.100.227:11434/` (por la IP de red, no por localhost) | "Ollama is running" ✅ | 04-ollama-version-modelos-red.png |
| `GET http://192.168.100.227:11434/api/tags` | JSON con los 2 modelos ✅ | 04-ollama-version-modelos-red.png |
| Proxy de Vite `/api` → Django | ✅ | — |

> **Seguridad:** la regla de firewall solo aplica al perfil **Privado**. En redes públicas (Wi-Fi de cafeterías, etc.) el puerto sigue cerrado. Ollama no tiene autenticación propia: nunca debe abrirse a Internet.

## 2. Manejo de fallas del motor de IA

Pruebas manuales con `curl` contra el sistema en marcha, con **Ollama apagado**:

| # | Caso | Código HTTP | Respuesta |
|---|---|---|---|
| 1 | Petición sin token | 401 | "Las credenciales de autenticación no se proveyeron." |
| 2 | Mensaje vacío | 400 | "Escribe una consulta válida." |
| 3 | `GET /estado/` con Ollama apagado | 200 | `{"ollama": false, ...}`: el chat muestra "Sin conexión" |
| 4 | `POST /chat/` con Ollama apagado | 503 | "El asistente no está disponible en este momento. Avisa a UTIC si el problema continúa." |
| 5 | `POST /chat/stream/` con Ollama apagado | 503 | El mismo mensaje controlado |

Pruebas automáticas (12/12 superadas, ver [bitácora](../bitacoras/2026-11-07-pruebas-automaticas-backend.md)): conexión rechazada, tiempo de espera agotado (504), modelo no instalado (503), streaming con Ollama caído y respuesta correcta en JSON.

**Resultado: cero errores 500 no controlados** ✅. En todos los casos de falla el backend devuelve un JSON con `ok: false` y un mensaje en español, y el resto de SIGTA sigue funcionando con normalidad.

Además, el reinicio de Ollama durante la sesión (para aplicar `OLLAMA_HOST`) no afectó al sistema: la primera consulta posterior tardó 48 s (recarga del modelo) y respondió correctamente.

## 3. Privacidad de los datos

| Usuario | Pregunta | Resultado |
|---|---|---|
| Técnico de la DAF | "¿Qué tickets tengo pendientes?" | "No tienes ninguno visible", correcto: la DAF no ve tickets de soporte en sus pantallas ✅ (12-consulta-texto-daf.png) |
| Usuario nuevo sin trámites | (prueba automática) | El contexto no incluye trámites de otros usuarios ✅ |
| Técnico de Soporte | "¿Tengo requerimientos de mantenimiento?" | "No tienes ninguno visible", correcto según su rol ✅ |

## 4. Navegador, micrófono y voz

| Prueba | Navegador | Resultado | Evidencia |
|---|---|---|---|
| El botón flotante abre el chat; el indicador muestra "En línea" | Chrome | ✅ | 12-consulta-texto-daf.png |
| Consulta por texto con respuesta (2,1 s) | Chrome | ✅ | 12-consulta-texto-daf.png |
| Permiso de micrófono y dictado transcrito en el chat | Chrome | ✅ | 14-consulta-voz.png |
| Respuesta leída en voz alta por los parlantes | Chrome | ✅ (confirmado por la tester) | — |
| Precisión del reconocimiento | Chrome | ⚠️ Se dijo "límite" y transcribió "nombre". La IA igual respondió el límite correcto | 14-consulta-voz.png |
| Firefox (sin SpeechRecognition) | Firefox | No probado. Por diseño, el botón 🎤 se oculta y el chat de texto funciona | — |
