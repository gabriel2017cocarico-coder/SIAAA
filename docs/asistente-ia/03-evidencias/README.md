# Evidencias de la integración del asistente de IA

Aquí se guardan las capturas, bitácoras y reportes de las pruebas de calidad.

## Estructura

```
03-evidencias/
├── capturas/        Imágenes PNG referenciadas en los manuales
├── bitacoras/       Registros diarios de trabajo y logs exportados
└── reportes/        Reportes entregados por cada integrante del Grupo B
```

## Convención de nombres

**Capturas:** `NN-descripcion-corta.png` (minúsculas, sin espacios ni tildes)

| Rango | Tema |
|---|---|
| 01–09 | Instalación de Ollama, red y modelo (manual técnico) |
| 10–19 | Interfaz del asistente (manual de usuario) |
| 20–39 | Pruebas E2E y de voz (Tte. Kantuta) |
| 40–59 | Rendimiento (Tte. Carballo) |
| 60–79 | Integración y red (Víctor Hugo) |

**Bitácoras:** `AAAA-MM-DD-responsable.md`, por ejemplo `2026-11-10-barrios.md`

**Reportes:**
- `reportes/matriz-pruebas-funcionales.md` (Tte. Kantuta)
- `reportes/reporte-rendimiento.md` (Tte. Carballo)
- `reportes/reporte-integracion.md` (Víctor Hugo)

## Evidencias recopiladas

| Archivo | Contenido |
|---|---|
| `capturas/03-firewall-regla.png` | Regla de entrada TCP 11434 (PowerShell como administrador) |
| `capturas/04-ollama-version-modelos-red.png` | `ollama --version`, `ollama list` y `/api/tags` accedidos por la IP de red |
| `capturas/12-consulta-texto-daf.png` | Chat abierto, indicador "En línea", consulta por texto y privacidad por rol (DAF) |
| `capturas/14-consulta-voz.png` | Consulta dictada por micrófono y respuesta (también leída en voz alta) |
| `bitacoras/2026-11-07-pruebas-automaticas-backend.md` | 12 pruebas automáticas del backend |
| `reportes/matriz-pruebas-funcionales.md` | Matriz de 40 consultas, voz y evolución del ajuste |
| `reportes/reporte-rendimiento.md` | Latencia, RAM y CPU consolidados |
| `reportes/reporte-integracion.md` | Red, fallas de Ollama, privacidad y navegador |
| `reportes/rendimiento-*.md` | Salida completa de cada corrida del banco de preguntas (iteraciones 1 a 5) |

## Plantilla de bitácora

```markdown
# Bitácora AAAA-MM-DD: <responsable>

**Tarea:** <qué se trabajó>
**Equipo:** <PC / VM, SO, RAM>

## Actividades
- HH:MM: <acción realizada>

## Resultados
- <qué funcionó, con la captura asociada>

## Problemas y solución
| Problema | Solución | Estado |
|---|---|---|
|  |  |  |
```
