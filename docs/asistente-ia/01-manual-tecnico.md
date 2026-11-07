# Manual técnico: Asistente de IA local de SIGTA

**Sistema:** SIGTA (Sistema Integral de Gestión de Tickets y Aprobaciones)
**Institución:** Escuela Militar de Ingeniería, Unidad Académica Santa Cruz
**Componente:** Asistente de IA local (Ollama + modelo `sigta-ai`) con interacción por texto y voz
**Versión del documento:** 1.0
**Fecha:** 07/11/2026
**Elaborado por:** Paola García

---

## 1. Objetivo

Describir la arquitectura, los servicios, los puertos y la configuración necesarios para instalar, operar y mantener el asistente de inteligencia artificial integrado en SIGTA. El asistente responde consultas sobre el sistema y sobre su estado operativo (tickets, requerimientos de mantenimiento y solicitudes de compra) mediante un modelo de lenguaje que se ejecuta **localmente**, sin enviar información a servicios externos.

## 2. Alcance

Incluye:
- El motor Ollama y el modelo especializado `sigta-ai`.
- El módulo backend `asistente` (Django) y su endpoint `POST /api/asistente/chat/`.
- El componente frontend `AsistenteVozModal.vue` (Vue 3), con reconocimiento y síntesis de voz.

No incluye el funcionamiento general de SIGTA, que está documentado en `ARQUITECTURA.txt` en la raíz del repositorio.

## 3. Arquitectura de la integración

### 3.1 Componentes

| Componente | Tecnología | Puerto | Función |
|---|---|---|---|
| Frontend (SPA) | Vue 3.5 + Vite 8 | 5173 | Interfaz del chat, micrófono (STT) y voz (TTS) |
| Backend (API REST) | Django + Django REST Framework | 8000 | Autenticación, armado del contexto y conexión con Ollama |
| Base de datos | SQLite 3 (`backend/db.sqlite3`) | (archivo) | Datos operativos de SIGTA |
| Motor de IA | Ollama | 11434 | Inferencia del modelo `sigta-ai` |
| Modelo | `sigta-ai` (sobre `llama3.2:3b`) | — | Generación de respuestas en español |

> **Nota sobre la base de datos:** el plan de implementación menciona PostgreSQL, pero SIGTA usa **SQLite 3** (ver `backend/config/settings.py`, `DATABASES`). Las consultas del asistente usan el ORM de Django, así que funcionan igual con cualquiera de los dos motores.

### 3.2 Diagrama general

```
 ┌────────────────────────────┐
 │  NAVEGADOR (Chrome / Edge) │
 │  Vue 3 · puerto 5173       │
 │  ┌──────────────────────┐  │
 │  │ AsistenteVozModal.vue│  │   Web Speech API:
 │  │  🎤 STT   🔊 TTS      │  │   voz → texto y texto → voz
 │  └──────────┬───────────┘  │   (procesado en el navegador)
 └─────────────┼──────────────┘
               │ POST /api/asistente/chat/
               │ Authorization: Token <clave>
               ▼
 ┌────────────────────────────┐        ┌──────────────────────┐
 │  BACKEND Django · 8000     │  ORM   │  SQLite              │
 │  app "asistente"           │ ─────► │  db.sqlite3          │
 │   views.py    (endpoint)   │ ◄───── │  tickets, mant.,     │
 │   contexto.py (datos)      │        │  compras, usuarios   │
 │   servicios.py (cliente)   │        └──────────────────────┘
 └─────────────┬──────────────┘
               │ POST http://<host>:11434/api/generate
               ▼
 ┌────────────────────────────┐
 │  OLLAMA · puerto 11434     │
 │  modelo sigta-ai           │
 │  (base llama3.2:3b)        │
 └────────────────────────────┘
```

### 3.3 Ciclo de vida de una consulta

1. **Entrada:** el usuario escribe su pregunta o pulsa el micrófono del botón flotante.
2. **Voz a texto (STT):** si la consulta es por voz, la Web Speech API del navegador la transcribe a texto en español (`es-ES` / `es-BO`).
3. **Petición:** el frontend envía `POST /api/asistente/chat/` con el texto y el token de sesión del usuario.
4. **Autenticación:** Django valida el token con `ExpiringTokenAuthentication` (12 horas de validez; rechaza usuarios inactivos).
5. **Contexto:** `contexto.py` consulta la base de datos y obtiene **solo la información que el usuario tiene permiso de ver** según sus roles.
6. **Armado del prompt:** Django une el mensaje del usuario con el contexto operativo y lo envía a Ollama.
7. **Inferencia:** Ollama genera la respuesta con el modelo `sigta-ai`.
8. **Respuesta:** Django devuelve un JSON estructurado al frontend.
9. **Texto a voz (TTS):** el frontend muestra la respuesta en el chat y la lee en voz alta con `window.speechSynthesis`.

## 4. Requisitos del equipo anfitrión

| Recurso | Mínimo recomendado | Equipo usado en las pruebas |
|---|---|---|
| Sistema operativo | Windows 10/11 64 bits | Windows 11 Home |
| Memoria RAM | 8 GB (4 GB libres para el modelo) | 15,3 GB (Ollama usa ~4 GB en inferencia) |
| Procesador | 4 núcleos, x86-64 con AVX2 | AMD Ryzen 7 7730U (8 núcleos / 16 hilos) |
| GPU | Opcional (acelera la inferencia) | Radeon integrada: la inferencia se hace con el procesador |
| Disco | ~3 GB libres para el modelo | 4 GB (modelo base + sigta-ai) |
| Navegador | Google Chrome o Microsoft Edge actualizados | — |

> Sin GPU el modelo corre solo con el procesador y las respuestas tardan más. Ver la sección 10 (rendimiento).

## 5. Instalación y configuración de Ollama

### 5.1 Instalación

1. Descargar el instalador oficial desde https://ollama.com/download (Windows), o instalarlo con `winget install --id Ollama.Ollama -e` (método usado).
2. Ejecutar el instalador.
3. Verificar en una terminal:
   ```powershell
   ollama --version
   ```
   Resultado obtenido: `ollama version is 0.40.15`
   Evidencia: `03-evidencias/capturas/04-ollama-version-modelos-red.png`

### 5.2 Servicio en segundo plano

Ollama queda corriendo como servicio en la bandeja del sistema. Para comprobarlo:
```powershell
curl http://127.0.0.1:11434/
# Respuesta esperada: "Ollama is running"
```
> La aplicación de escritorio de Ollama inicia el servicio automáticamente al abrirse. Para reiniciarlo: clic derecho en el icono de la llama (junto al reloj) → **Quit Ollama**, y volver a abrirlo desde el menú Inicio.

### 5.3 Red: variable OLLAMA_HOST

Para aceptar conexiones desde otros equipos de la red local o desde la máquina virtual (método usado, variable de usuario persistente):
```powershell
[Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'User')
```
Después hay que **cerrar y volver a abrir Ollama** para que tome la variable.

> **Seguridad:** `0.0.0.0` expone Ollama a toda la red local y Ollama no tiene autenticación propia. Si el backend Django corre en el mismo equipo que Ollama, se recomienda dejar `127.0.0.1:11434`. Usar `0.0.0.0` solo cuando el backend esté en otra máquina (por ejemplo, la VM) y limitar el firewall a esa IP.
> En la implementación entregada, Django y Ollama corren en el mismo equipo (`OLLAMA_URL=http://127.0.0.1:11434`). Se configuró igual `0.0.0.0` y el firewall en perfil **Privado**, para que una VM o un equipo de la red local también pueda usarlo.

### 5.4 Firewall de Windows

Regla de entrada para el puerto 11434 TCP (PowerShell como administrador):
```powershell
New-NetFirewallRule -DisplayName "Ollama 11434" -Direction Inbound `
  -Protocol TCP -LocalPort 11434 -Action Allow -Profile Private
```
Evidencia: `03-evidencias/capturas/03-firewall-regla.png` (Enabled: True, Inbound, Allow, Private).

Equivalente en Símbolo del sistema (CMD):
```
netsh advfirewall firewall add rule name="Ollama 11434" dir=in action=allow protocol=TCP localport=11434 profile=private
```

### 5.5 Verificación de conectividad

Desde el equipo de desarrollo:
```powershell
curl http://<IP_ANFITRION>:11434/api/tags
```
IP del anfitrión usada: `192.168.100.227`
Resultado: `Ollama is running` en `/` y un JSON con `sigta-ai:latest` y `llama3.2:3b` en `/api/tags` (HTTP 200).
Evidencia: `03-evidencias/capturas/04-ollama-version-modelos-red.png`

## 6. Modelo especializado `sigta-ai`

### 6.1 Modelo base

```powershell
ollama pull llama3.2:3b
```

### 6.2 Modelfile

El archivo `Modelfile` está en la raíz del repositorio. Configura la identidad y el comportamiento del asistente.

> **Precisión de términos:** el Modelfile **no reentrena** el modelo (no modifica sus pesos). Lo **especializa por configuración**: define su rol (instrucciones del sistema) y sus parámetros de inferencia. El conocimiento actualizado del sistema le llega en cada consulta a través del contexto que arma el backend (sección 7.3).

Parámetros definidos:

| Parámetro | Valor | Motivo |
|---|---|---|
| `FROM` | `llama3.2:3b` | Modelo ligero con buen soporte de español |
| `temperature` | `0.3` | Respuestas precisas y estables, con menos invención |
| `top_p` | `0.9` | Limita las palabras poco probables |
| `repeat_penalty` | `1.1` | Evita repeticiones |
| `num_ctx` | `4096` | Ventana de contexto: instrucciones + datos del usuario + pregunta (~2.500 tokens) |
| `MESSAGE` | 3 ejemplos | Ejemplos de respuesta (few-shot) que enseñan brevedad y corrigen errores frecuentes |
| `SYSTEM` | Ver 6.3 | Identidad del asistente de la EMI |

### 6.3 Instrucciones del sistema (resumen)

El texto completo está en el `Modelfile` de la raíz del repositorio. Sus secciones son:

| Sección | Contenido |
|---|---|
| REGLAS | Responder en español, breve y sin símbolos (se lee en voz alta); usar solo los datos entregados; no inventar; no revelar contraseñas; no aprobar trámites |
| GUÍA DE USO | Pasos reales de la interfaz: Inicio → Registrar solicitud, Mis solicitudes, verificaciones, Notificaciones |
| QUÉ ES SIGTA | Los 3 procesos, sus códigos (SOP, MTO, CMP), responsables y estados |
| SIGNIFICADO DE ESTADOS | Definición de los estados más consultados |
| ROLES | Los 12 roles del sistema |
| ORIENTACIÓN DE SOPORTE BÁSICO | Verificaciones seguras según el tipo de falla y cuándo registrar ticket o requerimiento |

Resumen de su enfoque:
- Identidad: asistente técnico de SIGTA de la EMI, Unidad Académica Santa Cruz.
- Áreas: soporte técnico (tickets UTIC), mantenimiento (Servicios Generales), compras de Caja Chica.
- Reglas: responder siempre en español, de forma breve y clara; usar solo los datos del contexto entregado; si no sabe algo, decirlo sin inventar.

### 6.4 Compilación y verificación

```powershell
ollama create sigta-ai -f ./Modelfile
ollama list
ollama run sigta-ai "¿Qué es SIGTA y qué procesos gestiona?"
```
Resultado de la prueba en consola: *"SIGTA es una aplicación web que gestiona tres procesos administrativos conectados: Soporte Técnico, Mantenimiento y Compras por Caja Chica…"*
Evidencia: `03-evidencias/capturas/04-ollama-version-modelos-red.png` (`ollama list`).

> **Ajuste iterativo:** el Modelfile se mejoró en 5 iteraciones medidas con el banco de 20 preguntas (ver `03-evidencias/reportes/matriz-pruebas-funcionales.md`, sección 4).

## 7. Módulo backend `asistente`

### 7.1 Estructura

```
backend/asistente/
├── __init__.py
├── apps.py
├── servicios.py   Cliente HTTP hacia Ollama (tiempos de espera y errores)
├── contexto.py    Consultas ORM con el estado operativo, filtradas por rol
├── views.py       Endpoints estado/, chat/ y chat/stream/
├── urls.py        Rutas de la app
└── tests.py       12 pruebas automáticas (python manage.py test asistente)
```
Registrada en `backend/config/settings.py` → `INSTALLED_APPS`, y montada en `backend/config/urls.py` bajo `api/asistente/`.

`servicios.py` usa solo la librería estándar de Python (`urllib`), así que **no agrega dependencias** a `requirements.txt`.

### 7.2 Configuración

Definidas en `backend/config/settings.py`. Todas se pueden cambiar con variables de entorno sin tocar el código:

| Variable (settings / entorno) | Valor por defecto | Descripción |
|---|---|---|
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Dirección del motor Ollama. Si está en otro equipo: `http://<IP>:11434` |
| `OLLAMA_MODELO` | `sigta-ai` | Modelo que se usa |
| `OLLAMA_TIMEOUT` | `90` segundos | Tiempo máximo de espera de la respuesta |
| `OLLAMA_KEEP_ALIVE` | `30m` | Tiempo que el modelo permanece cargado en RAM entre consultas |
| `OLLAMA_MAX_TOKENS` | `300` | Longitud máxima de cada respuesta |
| `ASISTENTE_MAX_CARACTERES` | `1000` | Longitud máxima de la pregunta |

### 7.3 Contexto operativo y privacidad

`contexto.py` arma un resumen del estado del sistema que se adjunta a cada consulta: fecha, usuario y roles efectivos, conteo por estado y los 6 expedientes activos más recientes de cada módulo (soporte, mantenimiento y compras), además del límite de Caja Chica configurado.

**Cómo se garantiza la privacidad:** `contexto.py` no reescribe las reglas de visibilidad. Ejecuta el mismo `get_queryset()` de los ViewSets que alimentan las bandejas del sistema (`TicketViewSet`, `RequerimientoMantenimientoViewSet` y `SolicitudCompraViewSet`). Por eso **el asistente ve exactamente lo mismo que el usuario ve en sus pantallas**, y si una regla de visibilidad cambia en el sistema, el asistente la respeta automáticamente.

| Rol | Datos que recibe el asistente (igual que sus bandejas) |
|---|---|
| Usuario (solicitante) | Solo sus propios tickets, requerimientos y solicitudes de compra |
| Técnico de Soporte | Tickets asignados a él o en los que participa como apoyo |
| Jefe UTIC | Todos los tickets de soporte |
| Jefe / Técnico de Mantenimiento | Requerimientos de mantenimiento según su rol |
| DAF / Almacén / Tesorería / Director | Solicitudes de compra con permiso `VER_COMPRAS` |
| Admin (superuser) | Solo administra usuarios: no ve trámites |

Verificado en la prueba automática `test_usuario_sin_tramites_no_ve_tramites_ajenos`.

### 7.4 Contrato de los endpoints

| Método y ruta | Uso |
|---|---|
| `GET /api/asistente/estado/` | Indica si Ollama responde y si el modelo está instalado (indicador "En línea" del chat) |
| `POST /api/asistente/chat/` | Respuesta completa en JSON (endpoint exigido por el plan) |
| `POST /api/asistente/chat/stream/` | La misma respuesta, pero enviada a medida que se genera (la usa el chat) |

> **Por qué hay un endpoint con streaming:** en un equipo sin GPU, la respuesta completa puede tardar varios segundos. Con streaming el texto empieza a aparecer apenas el modelo genera la primera palabra, y el usuario no se queda mirando una pantalla vacía.

El campo opcional `historial` (los últimos 4 mensajes) permite preguntas de seguimiento como "¿y quién lo atiende?".

**Petición**
```http
POST /api/asistente/chat/
Authorization: Token <clave>
Content-Type: application/json

{
  "mensaje": "¿Cuántos tickets tengo pendientes?",
  "historial": [ { "rol": "usuario", "texto": "..." }, { "rol": "asistente", "texto": "..." } ]
}
```

**Respuesta correcta de `/chat/` (200)**
```json
{
  "ok": true,
  "respuesta": "Tienes 2 tickets pendientes: ...",
  "modelo": "sigta-ai",
  "duracion_ms": 3120,
  "metricas": { "total_ms": 3050, "carga_modelo_ms": 12, "tokens_respuesta": 48, "tokens_por_segundo": 11.2 }
}
```

**Respuesta de `/chat/stream/` (200, `application/x-ndjson`)**: una línea JSON por evento:
```
{"texto": "Tienes "}
{"texto": "2 tickets"}
{"fin": true, "modelo": "sigta-ai", "duracion_ms": 3120, "primer_fragmento_ms": 900, "metricas": {...}}
```
Si Ollama falla antes de empezar, `/chat/stream/` responde con el mismo JSON de error y el mismo código (503/504) que `/chat/`. Si falla a mitad de la respuesta, envía la línea `{"error": "..."}`.

**Respuestas de error controladas**

| Código | Caso | Mensaje al usuario |
|---|---|---|
| 400 | Mensaje vacío o demasiado largo | "Escribe una consulta válida." |
| 401 | Token ausente o vencido | (el frontend redirige al login) |
| 502 | Ollama devolvió un error inesperado | "El asistente tuvo un problema al generar la respuesta." |
| 503 | Ollama apagado o inalcanzable | "El asistente no está disponible en este momento. Avisa a UTIC…" |
| 503 | Modelo `sigta-ai` no creado | "El modelo de IA no está instalado en el servidor. Avisa a UTIC." |
| 504 | Ollama tardó más que `OLLAMA_TIMEOUT` | "El asistente tardó demasiado en responder…" |

> Criterio de calidad: ante una caída de Ollama el backend **nunca** debe devolver un error 500 no controlado.

## 8. Componente frontend `AsistenteVozModal.vue`

### 8.1 Ubicación

- Componente: `frontend/src/components/AsistenteVozModal.vue`
- Integración global: `frontend/src/App.vue` (junto a `<RouterView />`), así está disponible en todas las vistas.
- **Solo aparece con sesión iniciada**: se oculta en el login, en la recuperación de contraseña y en el cambio obligatorio de contraseña. Al cerrar sesión, la conversación se borra.

### 8.2 Funciones

| Función | API del navegador | Configuración |
|---|---|---|
| Voz a texto (STT) | `SpeechRecognition` / `webkitSpeechRecognition` | `lang = 'es-ES'`, resultados parciales visibles mientras se habla; al terminar de hablar la pregunta se envía sola |
| Texto a voz (TTS) | `window.speechSynthesis` + `SpeechSynthesisUtterance` | Elige una voz en español (prefiere es-BO, luego Google/Microsoft). Lee por oraciones, porque Chrome corta las locuciones largas |
| Envío de mensajes | `fetch` a `/api/asistente/chat/stream/` con `Authorization: Token ${localStorage.getItem('sigta_token')}` | Lee la respuesta en streaming (`ReadableStream`) |
| Estado del servicio | `fetch` a `/api/asistente/estado/` al abrir el chat | Indicador "En línea" / "Sin conexión" / "Modelo no instalado" |

### 8.3 Controles de la interfaz

| Control | Comportamiento |
|---|---|
| Botón flotante (esquina inferior derecha, azul con borde mostaza) | Abre el chat |
| 🎤 Micrófono | Inicia o detiene el dictado. En rojo y con pulso mientras escucha |
| Campo de texto + ➤ | Envía la pregunta escrita (también con Enter) |
| 🔊 / 🔇 | Activa o silencia la lectura en voz alta (la preferencia se recuerda) |
| 🔁 | Vuelve a leer la última respuesta |
| ✕ o tecla Esc | Cierra el chat y detiene el micrófono y el audio |
| Sugerencias iniciales | Preguntas de ejemplo con un clic |

Errores del micrófono que se muestran al usuario: permiso denegado, no se detectó voz, no hay micrófono y falta de internet (el reconocimiento de Chrome/Edge lo necesita).

### 8.4 Compatibilidad y restricciones

| Navegador | Voz a texto | Texto a voz |
|---|---|---|
| Google Chrome | Sí | Sí |
| Microsoft Edge | Sí | Sí |
| Mozilla Firefox | **No** (no implementa SpeechRecognition) | Sí |
| Safari | Parcial | Sí |

- El micrófono solo funciona en un **contexto seguro**: `http://localhost`, `http://127.0.0.1` o `https://`. Si se accede por la IP de la red (`http://192.168.x.x:5173`), el navegador bloquea el micrófono.
- En Chrome y Edge el reconocimiento de voz usa un servicio en la nube del navegador. **El audio sale del equipo** aunque el modelo de IA sea local. Esto debe tenerse en cuenta en la política de privacidad.
- Si el usuario niega el permiso del micrófono, el chat de texto debe seguir funcionando.

## 9. Puesta en marcha completa

Orden de arranque:

```powershell
# 1. Ollama (si no está corriendo como servicio)
ollama serve

# 2. Backend
cd backend
python manage.py runserver 127.0.0.1:8000

# 3. Frontend
cd frontend
npm run dev
```
Abrir http://localhost:5173, iniciar sesión y pulsar el botón flotante del asistente.

## 10. Rendimiento

Detalle completo: `03-evidencias/reportes/reporte-rendimiento.md` (40 consultas sucesivas, 2 roles).

| Métrica | Meta | Resultado |
|---|---|---|
| Tiempo promedio de respuesta completa | < 4 s | 8,7 s ❌ (mediana 7,5 s; 2,2 s a 22,8 s) |
| Tiempo hasta el primer fragmento de la respuesta (lo que percibe el usuario) | < 4 s | **0,85 s** ✅ |
| RAM usada por Ollama durante la inferencia | Sin saturar el equipo | ~4,0 GB máx. (26 % de la RAM) ✅ |
| CPU durante la inferencia | — | ~49 % promedio ✅ |
| Consultas fallidas | 0 | 0 de 40 ✅ |

> El tiempo depende mucho del hardware. Sin GPU, un modelo de 3B parámetros puede superar los 4 segundos en respuestas largas.

### 10.1 Optimizaciones aplicadas

Medición inicial en el equipo de pruebas (Ryzen 7 7730U, sin GPU dedicada): la primera consulta tardaba **23,9 s**, de los cuales **16,4 s** eran para procesar el prompt (2.535 tokens: instrucciones del sistema y datos del usuario). Se aplicaron estas optimizaciones:

| Optimización | Dónde | Efecto |
|---|---|---|
| **Caché de prefijo de Ollama**: el contexto se ordena de lo más estable a lo más cambiante (la fecha y hora van al final) | `contexto.py` | Ollama reutiliza el prompt ya procesado y solo lee la pregunta nueva |
| **Precalentamiento**: al abrir el chat, `GET /estado/` procesa en segundo plano los datos del usuario mientras escribe | `views.py`, `servicios.precalentar()` | La primera pregunta también aprovecha el caché |
| **Streaming**: la respuesta se envía palabra por palabra | `/chat/stream/` + `AsistenteVozModal.vue` | El usuario ve texto en menos de 1 s |
| **`keep_alive = 30m`** | `settings.py` | El modelo no se descarga de la RAM entre consultas |
| **`num_predict = 300`** e instrucción de responder en máximo 5 oraciones | `settings.py`, `Modelfile` | Respuestas breves, más rápidas y aptas para leerse en voz alta |

**Resultado:** la lectura del prompt bajó de **16,4 s a 0,6 s** y la respuesta completa de **23,9 s a ~5 s**.

## 11. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| "El asistente no está disponible" | Ollama apagado | Iniciar Ollama y comprobar con `curl http://127.0.0.1:11434/` |
| `curl` a `:11434` falla desde otro equipo | `OLLAMA_HOST` o firewall | Revisar las secciones 5.3 y 5.4 |
| `model 'sigta-ai' not found` | Modelo no creado en ese equipo | `ollama create sigta-ai -f ./Modelfile` |
| El botón del micrófono no aparece o no responde | Navegador sin soporte o sitio no seguro | Usar Chrome o Edge en `localhost` |
| El micrófono no transcribe | Permiso denegado | Candado de la barra de direcciones → Micrófono → Permitir |
| No se oye la respuesta | Volumen, sin voz en español o audio silenciado en el chat | Revisar el volumen y el botón de silencio del asistente |
| La primera respuesta tarda mucho | El modelo se está cargando en memoria | Normal en la primera consulta; las siguientes son más rápidas |

## 12. Referencias

- `ARQUITECTURA.txt`: arquitectura general de SIGTA.
- Documentación de Ollama: https://github.com/ollama/ollama/tree/main/docs
- Web Speech API (MDN): https://developer.mozilla.org/es/docs/Web/API/Web_Speech_API
