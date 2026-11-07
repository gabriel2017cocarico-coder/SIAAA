# Informe final de integración del componente de Inteligencia Artificial

**Proyecto:** SIGTA, Escuela Militar de Ingeniería, Unidad Académica Santa Cruz
**Componente:** Asistente de IA local con Ollama (texto y voz)
**Fecha:** 07/11/2026
**Elaborado por:** Paola García

---

## 1. Resumen ejecutivo

Se integró en SIGTA un asistente virtual, **SIGTA-AI**, que se ejecuta **localmente** con Ollama y el modelo especializado `sigta-ai` (basado en `llama3.2:3b`). Responde por texto y por voz sobre el funcionamiento del sistema y sobre el estado real de los trámites de cada usuario. Se completaron los seis pasos del plan: instalación de Ollama, modelo especializado, red y firewall, backend Django, frontend Vue con voz bidireccional, y pruebas integrales.

El sistema funciona de extremo a extremo y **respeta los permisos de cada rol**: el asistente solo ve lo que el usuario ve en sus pantallas. Ante una caída del motor de IA responde con mensajes controlados, **sin errores 500**. El texto de la respuesta empieza a aparecer en **0,85 s** en promedio.

Hay dos criterios que **no se alcanzaron por completo**, y se explican con transparencia en la sección 5: la precisión fue de **87,5 %** (la meta era 95 %) y el tiempo de respuesta *completa* fue de **8,7 s** (la meta era menos de 4 s). Ambos se deben al tamaño del modelo y a la ausencia de una GPU dedicada en el equipo anfitrión.

## 2. Objetivo

Integrar en SIGTA un asistente de inteligencia artificial que se ejecute localmente mediante Ollama, capaz de responder consultas sobre el sistema y su estado operativo, por texto y por comandos de voz bidireccionales.

## 3. Ejecución del trabajo

> El plan original distribuía el trabajo entre ocho integrantes. **Todas las tareas, técnicas y de calidad, fueron ejecutadas por Paola.** La tabla mantiene la división del plan para mostrar que cada responsabilidad quedó cubierta.

| Responsabilidad del plan | Asignada en el plan a | Ejecutada por | Estado |
|---|---|---|---|
| Instalación de Ollama, red y firewall | Barrios | Paola | ✅ |
| Modelfile y modelo `sigta-ai` | Caillavi | Paola | ✅ |
| Backend Django, endpoint `/api/asistente/chat/` | Cocarico | Paola | ✅ |
| Frontend Vue, chat, STT y TTS | Deybi | Paola | ✅ |
| Pruebas E2E y de voz | Tte. Kantuta | Paola | ✅ |
| Pruebas de rendimiento | Tte. Carballo | Paola | ✅ |
| Pruebas de integración y red | Víctor Hugo | Paola | ✅ |
| Documentación y evidencias | Paola | Paola | ✅ |

## 4. Solución implementada

Detalle completo en el [manual técnico](01-manual-tecnico.md).

| Capa | Implementación |
|---|---|
| **Motor de IA** | Ollama 0.40.15, puerto 11434, `OLLAMA_HOST=0.0.0.0:11434`, regla de firewall TCP 11434 en perfil Privado |
| **Modelo** | `sigta-ai` sobre `llama3.2:3b` (Q4_K_M, 2,0 GB), temperatura 0.3, `num_ctx` 4096, instrucciones del sistema con los 3 procesos, estados, roles y guía de uso, más 3 ejemplos de respuesta |
| **Backend** | App Django `asistente`: `servicios.py` (cliente HTTP con manejo de errores, sin dependencias nuevas), `contexto.py` (datos reales filtrados por permisos), `views.py` (endpoints `estado/`, `chat/` y `chat/stream/`), `tests.py` (12 pruebas) |
| **Frontend** | `AsistenteVozModal.vue`, global en `App.vue`: botón flotante, chat con streaming, micrófono (Web Speech API, es-ES), lectura en voz alta (SpeechSynthesis), silenciar y repetir |
| **Base de datos** | SQLite 3 (el plan menciona PostgreSQL, pero el sistema usa SQLite; el ORM de Django hace que el código funcione igual con ambos) |

### Decisiones técnicas destacadas

1. **Privacidad por diseño.** `contexto.py` no reescribe las reglas de acceso: reutiliza el `get_queryset()` de las mismas vistas que alimentan las bandejas del sistema. Así el asistente ve exactamente lo que el usuario ve.
2. **Streaming.** Además del endpoint `/chat/` que pide el plan, se agregó `/chat/stream/`, para que el texto aparezca mientras se genera.
3. **Caché de prefijo y precalentamiento.** Al ordenar el contexto de lo más estable a lo más cambiante, y al procesarlo cuando el usuario abre el chat, la lectura del prompt bajó de **16,4 s a 0,6 s**.
4. **Ajuste iterativo medido.** El Modelfile se mejoró en 5 iteraciones, cada una evaluada con un banco de 20 preguntas.

## 5. Cumplimiento de criterios de aceptación

| # | Criterio | Cumple | Evidencia |
|---|---|---|---|
| 1 | `ollama list` responde en el anfitrión | ✅ | capturas/04-ollama-version-modelos-red.png |
| 2 | `http://<IP>:11434/` responde 200 desde el entorno de desarrollo | ✅ (por 192.168.100.227) | capturas/04-ollama-version-modelos-red.png |
| 3 | El puerto 11434 no está bloqueado | ✅ | capturas/03-firewall-regla.png |
| 4 | `Modelfile` versionado en la raíz del proyecto | ✅ | `/Modelfile` |
| 5 | `sigta-ai` aparece en la lista de modelos | ✅ | capturas/04-ollama-version-modelos-red.png |
| 6 | Las respuestas reflejan la estructura de SIGTA | ✅ | reportes/matriz-pruebas-funcionales.md |
| 7 | El endpoint responde JSON estructurado | ✅ | bitacoras/2026-11-07-pruebas-automaticas-backend.md |
| 8 | Maneja tiempos de espera con Ollama | ✅ (504 controlado, `OLLAMA_TIMEOUT` = 90 s) | reportes/reporte-integracion.md |
| 9 | Mensajes amigables ante cortes del servicio | ✅ | reportes/reporte-integracion.md |
| 10 | El botón flotante es visible y abre el chat | ✅ | capturas/12-consulta-texto-daf.png |
| 11 | El micrófono transcribe la voz a texto | ✅ | capturas/14-consulta-voz.png |
| 12 | Las respuestas se muestran y se leen en voz alta | ✅ | capturas/14-consulta-voz.png |
| 13 | ≥ 95 % de consultas con respuesta satisfactoria | ❌ **87,5 %** (35/40) | reportes/matriz-pruebas-funcionales.md |
| 14 | Flujo continuo de micrófono a audio | ✅ | reportes/matriz-pruebas-funcionales.md §6 |
| 15 | Tiempo promedio de respuesta < 4 s | ⚠️ Primer fragmento: **0,85 s** ✅ · Respuesta completa: **8,7 s** ❌ | reportes/reporte-rendimiento.md |
| 16 | RAM de Ollama controlada | ✅ ~4,0 GB (26 % del equipo) | reportes/reporte-rendimiento.md |
| 17 | Cero errores 500 ante caída de Ollama | ✅ | reportes/reporte-integracion.md |
| 18 | Consola del navegador sin excepciones | ⚠️ No se registró formalmente; las pruebas manuales no mostraron fallas visibles | — |
| 19 | Manuales técnico y de usuario con capturas | ✅ | 01-manual-tecnico.md, 02-manual-usuario.md |
| 20 | Documentación consolidada en el repositorio | ✅ | docs/asistente-ia/ |

**Resumen: 17 criterios cumplidos, 2 parciales y 1 no cumplido.**

## 6. Resultados de las pruebas

### 6.1 Pruebas funcionales
40 consultas (20 preguntas × 2 roles): **35 correctas, 2 parciales y 3 incorrectas (87,5 %)**. Con el rol Técnico se llegó a 95 %. En seguridad (contraseñas, aprobaciones, preguntas fuera de tema, datos inexistentes) el resultado fue **10/10**. Los 3 errores ocurrieron al contar o seleccionar dentro de listas largas (el usuario de prueba tiene 43 requerimientos). Detalle: [matriz-pruebas-funcionales.md](03-evidencias/reportes/matriz-pruebas-funcionales.md).

### 6.2 Rendimiento
Primer fragmento en **0,85 s** promedio; respuesta completa en **8,7 s** promedio (mediana 7,5 s); ~9,3 tokens/s; RAM máxima 4,0 GB; CPU ~49 %; **0 fallos en 40 consultas seguidas**. Detalle: [reporte-rendimiento.md](03-evidencias/reportes/reporte-rendimiento.md).

### 6.3 Integración y red
Acceso por IP de red verificado. Con Ollama apagado, todas las rutas devuelven 401/400/503 controlados. 12/12 pruebas automáticas superadas. La privacidad por rol se verificó con DAF, Técnico y un usuario nuevo. Detalle: [reporte-integracion.md](03-evidencias/reportes/reporte-integracion.md).

## 7. Problemas encontrados y soluciones

| # | Problema | Solución aplicada | Estado |
|---|---|---|---|
| 1 | El entorno virtual `.venv` del backend se creó en otra PC y no funciona | Se usó el Python global con `requirements.txt` | ✅ |
| 2 | La primera respuesta tardaba 23,9 s (16,4 s solo en leer el prompt) | Caché de prefijo (fecha al final del contexto) + precalentamiento al abrir el chat → ~5 s | ✅ |
| 3 | El modelo inventaba pasos (p. ej. "el usuario asigna técnico y prioridad") | Guía de uso real y ejemplos de respuesta en el Modelfile | ✅ |
| 4 | El modelo copiaba los datos crudos con barras `\|` (se leían mal en voz alta) | Contexto redactado en frases naturales | ✅ |
| 5 | El modelo confundía "total" con "activos" | Totales y activos precalculados en el contexto | ✅ |
| 6 | El script de rendimiento medía mal la RAM (no incluía `llama-server`) y los contadores de CPU dependían del idioma de Windows | Se incluyó el proceso correcto y se calculó la CPU por tiempo de proceso | ✅ |
| 7 | El comando de firewall de PowerShell falló en CMD | Se ejecutó en PowerShell como administrador (también se documentó el equivalente `netsh`) | ✅ |
| 8 | Errores de conteo en listas largas | Mitigado parcialmente; ver recomendaciones | ⚠️ |

## 8. Limitaciones conocidas

- **Precisión en listas largas:** un modelo de 3B parámetros puede contar o seleccionar mal cuando un usuario tiene decenas de trámites.
- **Sin GPU**, la respuesta completa tarda varios segundos. La carga inicial del modelo tarda de 20 a 50 s.
- **Reconocimiento de voz:** solo funciona en Chrome y Edge, en `localhost` o HTTPS. En esos navegadores el audio se procesa en la nube del navegador (la IA sí es 100 % local). Puede transcribir mal algunas palabras (en las pruebas, "límite" se transcribió como "nombre").
- El asistente orienta e informa, pero no ejecuta acciones en el sistema.

## 9. Conclusiones y recomendaciones

**Conclusiones**
1. Es viable integrar un asistente de IA **100 % local** en SIGTA, sin enviar datos institucionales a servicios externos y sin costos de licencia, en una laptop sin GPU dedicada.
2. La arquitectura en capas (Vue → Django → Ollama) permitió que **la seguridad la controle el backend**: el modelo nunca accede a la base de datos y solo recibe los datos que el usuario puede ver.
3. El ajuste medido (5 iteraciones con métricas) es más efectivo que ajustar "a ojo": la precisión pasó de ~65 % a 87,5 % y la latencia percibida bajó a menos de 1 s.

**Recomendaciones para alcanzar las metas pendientes**
1. **Equipo con GPU** (NVIDIA con 4 GB o más): la respuesta completa bajaría a 1-3 s.
2. **Modelo más grande** (`llama3.1:8b` o `qwen2.5:7b`) para mejorar la precisión en conteos.
3. **Respuestas deterministas para cantidades:** que el backend responda directamente las preguntas "¿cuántos…?" con el ORM.
4. **Contexto por módulo:** enviar solo los datos del módulo al que se refiere la pregunta.

## 10. Anexos

- [Manual técnico](01-manual-tecnico.md)
- [Manual de usuario](02-manual-usuario.md)
- [Evidencias: capturas, bitácoras y reportes](03-evidencias/)
- Código: `Modelfile`, `backend/asistente/`, `frontend/src/components/AsistenteVozModal.vue`
