# Asistente de IA de SIGTA (Ollama): documentación

Documentación de la integración del asistente de inteligencia artificial local (Ollama + modelo `sigta-ai`), que se usa por texto y por voz dentro de SIGTA.

Implementación, pruebas y documentación: **Paola**.

## Contenido

| Documento | Descripción | Estado |
|---|---|---|
| [04-informe-final.md](04-informe-final.md) | **Informe final**: resultados, criterios de aceptación, problemas y conclusiones | ✅ Completo |
| [01-manual-tecnico.md](01-manual-tecnico.md) | Arquitectura, puertos, instalación, configuración, endpoints y rendimiento | ✅ Completo |
| [02-manual-usuario.md](02-manual-usuario.md) | Uso del asistente por texto y por voz, paso a paso | ✅ Completo |
| [03-evidencias/](03-evidencias/) | Capturas, bitácoras y reportes de pruebas | ✅ Completo |

## Resultados clave

| Indicador | Resultado |
|---|---|
| Criterios de aceptación | 17 cumplidos · 2 parciales · 1 no cumplido |
| Precisión (40 consultas, 2 roles) | 87,5 % (seguridad: 10/10) |
| Tiempo hasta el primer fragmento | 0,85 s |
| Respuesta completa | 8,7 s promedio (sin GPU) |
| Errores 500 ante caída de Ollama | 0 |
| Pruebas automáticas | 12/12 |

## Código de la integración

| Archivo | Función |
|---|---|
| `Modelfile` | Modelo especializado `sigta-ai` |
| `backend/asistente/` | App Django: `servicios.py`, `contexto.py`, `views.py`, `urls.py`, `tests.py`, `medir_rendimiento.py` |
| `frontend/src/components/AsistenteVozModal.vue` | Chat flotante con voz (integrado en `App.vue`) |

## Cómo ejecutar

```powershell
# 1. Ollama (abrir la aplicación) y crear el modelo una sola vez
ollama pull llama3.2:3b
ollama create sigta-ai -f ./Modelfile

# 2. Backend
cd backend; python manage.py runserver 127.0.0.1:8000

# 3. Frontend (otra terminal)
cd frontend; npm run dev

# Pruebas
cd backend; python manage.py test asistente
cd backend; python asistente/medir_rendimiento.py
```
