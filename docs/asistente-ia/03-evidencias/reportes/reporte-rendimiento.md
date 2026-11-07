# Reporte de rendimiento, latencia y uso de recursos

- **Fecha:** 07/11/2026
- **Herramienta:** `backend/asistente/medir_rendimiento.py` (mide de extremo a extremo: login → Django → Ollama → respuesta completa, y muestrea RAM y CPU de Ollama cada segundo)
- **Equipo anfitrión:** laptop con AMD Ryzen 7 7730U (8 núcleos / 16 hilos), 15,3 GB de RAM, gráficos integrados Radeon (**sin GPU dedicada**: la inferencia se hace con el procesador), Windows 11
- **Software:** Ollama 0.40.15 · modelo `sigta-ai` sobre `llama3.2:3b` (cuantización Q4_K_M, 2,0 GB)

## 1. Resultados finales (versión entregada)

40 consultas sucesivas, 20 por rol, sin pausas entre ellas:

| Métrica | Solicitante | Técnico | Meta | ¿Cumple? |
|---|---|---|---|---|
| Tiempo hasta el primer fragmento (promedio) | **0,9 s** | **0,8 s** | < 4 s | ✅ |
| Respuesta completa (promedio) | 8,6 s | 8,8 s | < 4 s | ❌ |
| Respuesta completa (mediana) | 7,7 s | 7,2 s | | |
| Respuesta completa (mínimo / máximo) | 2,6 s / 17,9 s | 2,2 s / 22,8 s | | |
| Velocidad de generación | 9,0 tokens/s | 9,6 tokens/s | | |
| RAM de Ollama (máximo) | 4.033 MB | 3.834 MB | Sin saturar | ✅ ~26 % de 15,3 GB |
| CPU de Ollama (promedio) | 49 % | 49 % | | ✅ el equipo sigue usable |
| Consultas fallidas | 0 de 20 | 0 de 20 | | ✅ |

Detalle por consulta: [rendimiento-20261107-1330-solicitante.md](rendimiento-20261107-1330-solicitante.md) · [rendimiento-20261107-1333-especialista.md](rendimiento-20261107-1333-especialista.md)

### Interpretación

- **Lo que percibe el usuario:** gracias al streaming, el texto empieza a aparecer en **menos de 1 segundo** en el 100 % de las consultas. Ese criterio se cumple.
- **La respuesta completa** tarda en promedio unos 8,7 s. No llega a la meta de 4 s porque, sin GPU, el modelo genera ~9-10 tokens por segundo y una respuesta típica tiene entre 40 y 200 tokens. Las respuestas cortas (datos puntuales) tardan 2-4 s; las explicaciones de procesos tardan 15-23 s.
- **Estabilidad:** 40 consultas seguidas sin errores, y con RAM y CPU estables durante toda la prueba.
- **Primera carga:** cuando Ollama se acaba de iniciar, la primera consulta tarda entre 19 y 48 s, porque carga el modelo en la RAM. Después se mantiene cargado 30 minutos (`keep_alive`).

## 2. Evolución de la latencia durante el ajuste

| Medición | Lectura del prompt | Respuesta completa | Cambio aplicado |
|---|---|---|---|
| Primera consulta sin optimizar | 16,4 s | 23,9 s | — |
| Con caché de prefijo y precalentamiento | 0,6 s | ~5 s | Contexto ordenado (la fecha al final) + precalentamiento al abrir el chat |
| Iteración 3 (20 preguntas) | — | 11,4 s prom. | Respuestas más largas y completas |
| Iteración 4 (20 preguntas) | — | 8,0 s prom. | Ejemplos de respuesta breves en el Modelfile |
| **Final (40 preguntas)** | — | **8,7 s prom.** | Definiciones de estados |

## 3. Recomendaciones

1. **Con GPU** (NVIDIA con 4 GB o más) la generación sube a 40-80 tokens/s, y la respuesta completa bajaría a 1-3 s. Así sí se cumple la meta de 4 s.
2. Reducir `OLLAMA_MAX_TOKENS` (hoy 300) acorta las respuestas más largas, pero algunas listas pueden quedar cortadas.
3. Mantener Ollama iniciado durante la jornada, para evitar la carga inicial de 20-50 s.
