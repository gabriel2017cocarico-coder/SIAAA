# Reporte de rendimiento del asistente SIGTA-AI

> **Iteración 1 (antes de ajustar el Modelfile).** El valor de RAM de este reporte es incorrecto: el script solo medía los procesos `ollama*` y no el proceso `llama-server`, que es el que carga el modelo (~2,8 GB). Se corrigió en la iteración 2.

- **Fecha:** 07/11/2026 13:09
- **Usuario de prueba:** solicitante@emi.edu.bo
- **Consultas:** 20 (20 exitosas, 0 fallidas)
- **Carga inicial del modelo (no incluida en el promedio):** 19.2 s
- **Recorrido medido:** navegador simulado -> Django `/api/asistente/chat/stream/` -> Ollama -> respuesta completa

## Resumen

| Métrica | Valor |
|---|---|
| Tiempo promedio hasta el primer fragmento | 0.7 s |
| Tiempo promedio de respuesta completa | 9.0 s |
| Tiempo mínimo / máximo | 2.3 s / 26.4 s |
| Mediana de respuesta completa | 7.0 s |
| Velocidad de generación promedio | 10.8 tokens/s |
| RAM de Ollama (promedio / máximo) | 189 MB / 209 MB |
| CPU de Ollama (promedio / máximo) | 0 % / 0 % |

## Detalle por consulta

| # | Categoría | Pregunta | 1er fragmento (s) | Total (s) | Tokens | OK |
|---|---|---|---|---|---|---|
| 1 | Sistema | ¿Qué es SIGTA y qué procesos gestiona? | 0.7 | 15.5 | 150 | ✅ |
| 2 | Sistema | ¿Cómo registro un ticket de soporte técnico? | 1.0 | 22.5 | 229 | ✅ |
| 3 | Sistema | ¿Qué diferencia hay entre un ticket de soporte y un requerimiento de mantenimiento? | 0.8 | 7.1 | 67 | ✅ |
| 4 | Sistema | ¿Cuáles son los pasos de una compra por Caja Chica? | 0.8 | 17.6 | 180 | ✅ |
| 5 | Sistema | ¿Qué significa el estado Pendiente de conformidad? | 0.7 | 7.3 | 70 | ✅ |
| 6 | Sistema | ¿Quién aprueba el desembolso de una compra? | 0.7 | 3.1 | 27 | ✅ |
| 7 | Datos | ¿Cuántos tickets de soporte tengo en total? | 0.6 | 2.3 | 19 | ✅ |
| 8 | Datos | ¿Qué tickets tengo activos ahora? | 0.9 | 10.1 | 98 | ✅ |
| 9 | Datos | ¿Qué técnico atiende mi ticket más reciente? | 0.6 | 4.6 | 44 | ✅ |
| 10 | Datos | ¿Tengo requerimientos de mantenimiento pendientes? | 0.7 | 5.4 | 52 | ✅ |
| 11 | Datos | ¿En qué estado están mis solicitudes de compra? | 0.6 | 26.4 | 272 | ✅ |
| 12 | Datos | ¿Cuál es el límite de Caja Chica? | 0.7 | 2.4 | 19 | ✅ |
| 13 | Soporte | Mi proyector no enciende, ¿qué hago? | 0.8 | 7.0 | 67 | ✅ |
| 14 | Soporte | Mi computadora está muy lenta, ¿qué puedo revisar? | 0.7 | 8.1 | 80 | ✅ |
| 15 | Soporte | Se fue la luz en mi aula, ¿a quién reporto? | 1.1 | 7.0 | 64 | ✅ |
| 16 | Límites | ¿Cuál es la contraseña del administrador? | 0.6 | 6.2 | 60 | ✅ |
| 17 | Límites | Aprueba mi solicitud de compra. | 0.5 | 7.6 | 76 | ✅ |
| 18 | Límites | ¿Quién ganó el último mundial de fútbol? | 0.7 | 5.7 | 54 | ✅ |
| 19 | Límites | Dame el ticket SOP-2099-9999. | 0.6 | 5.2 | 48 | ✅ |
| 20 | Límites | What is SIGTA? | 0.5 | 8.1 | 82 | ✅ |

## Respuestas obtenidas

**1. ¿Qué es SIGTA y qué procesos gestiona?**

> SIGTA es el Sistema Integral de Gestión de Tickets y Aprobaciones, una aplicación web que gestiona tres procesos administrativos conectados. Estos procesos son:
> 
> 1. Soporte Técnico: gestiona solicitudes de ayuda para equipos y dispositivos.
> 2. Mantenimiento: gestiona solicitudes de mantenimiento para la unidad académica.
> 3. Compras por Caja Chica: gestiona solicitudes de compra para artículos necesarios.
> 
> Estos procesos están diseñados para mejorar la eficiencia y la calidad del servicio en estos ámbitos, permitiendo a los usuarios gestionar de manera centralizada y organizada las solicitudes de ayuda, mantenimiento y compras.

**2. ¿Cómo registro un ticket de soporte técnico?**

> Para registrar un ticket de soporte técnico, el usuario debe seguir los siguientes pasos:
> 
> 1. Acceder a la sección de tickets de soporte técnico en SIGTA.
> 2. Hacer clic en "Crear ticket" y seleccionar el tipo de problema que está experimentando (por ejemplo, "Problema con equipo", "Problema con conexión", etc.).
> 3. Introducir información detallada sobre el problema, incluyendo la ubicación del equipo, la fecha y hora en que comenzó a ocurrir el problema, y cualquier error o mensaje de error que esté mostrando.
> 4. Seleccionar un técnico para asignar al ticket.
> 5. Agregar cualquier archivo adjunto relevante (por ejemplo, una captura de pantalla, un log de error, etc.).
> 6. Asignar la prioridad del ticket según su importancia y urgencia.
> 7. Crear el ticket y guardar los cambios.
> 
> Es importante mencionar que el usuario debe tener permisos suficientes para crear tickets de soporte técnico en SIGTA.

**3. ¿Qué diferencia hay entre un ticket de soporte y un requerimiento de mantenimiento?**

> Solicitante, un ticket de soporte es una solicitud de ayuda para resolver problemas técnicos en equipos o sistemas, mientras que un requerimiento de mantenimiento es una solicitud formal para realizar reparaciones o mejoras en infraestructura. Ambos requieren autorización y ejecución por parte de técnicos especializados.

**4. ¿Cuáles son los pasos de una compra por Caja Chica?**

> Solicitante, para realizar una compra por Caja Chica, sigue estos pasos:
> 
> 1.  Solicita un requerimiento de mantenimiento en SIGTA.
> 2.  El Jefe de Mantenimiento lo valida y prioriza.
> 3.  Si se requiere producto, se revisa en Almacén y si no hay, se deriva a compra.
> 4.  El Técnico de Mantenimiento ejecuta el trabajo y registra su informe.
> 5.  El usuario da conformidad.
> 6.  La Tesorería desembolsa fondos cuando el monto estimado supera el límite de Caja Chica (Bs 1500).
> 7.  Almacén y Compras compran, ingresa y despacha el producto.
> 8.  El Solicitante firma el acta de entrega.

**5. ¿Qué significa el estado Pendiente de conformidad?**

> El estado "Pendiente de conformidad" se refiere a un ticket de soporte técnico que requiere la conformidad del usuario para finalizar su solución. En otras palabras, el técnico ha completado las reparaciones o soluciones y ahora espera la aprobación del usuario para considerar el ticket cerrado.

**6. ¿Quién aprueba el desembolso de una compra?**

> Según los datos actuales del sistema, el desembolso de una compra se aprueba en la Tesorería.

**7. ¿Cuántos tickets de soporte tengo en total?**

> Solicitante, tienes un total de 18 tickets de soporte técnico.

**8. ¿Qué tickets tengo activos ahora?**

> Solicitante, actualmente tienes dos tickets de soporte técnico activos:
> 
> 1. SOP-2026-0015 "Proyectora no enciende" con estado Pendiente de informe final y prioridad Alta.
> 2. SOP-2026-0011 "rrrrrrr" con estado En ejecución y prioridad Media.
> 
> Ambos tienen fechas de vencimiento SLA correspondientes el 01/10/2026.

**9. ¿Qué técnico atiende mi ticket más reciente?**

> El técnico que atiende tu ticket más reciente, SOP-2026-0015 "Proyectora no enciende", es Técnico de Soporte Técnico.

**10. ¿Tengo requerimientos de mantenimiento pendientes?**

> Sí, hay Requerimientos de Mantenimiento activos más recientes en el sistema. Para ver los detalles, revisa la pantalla correspondiente y busca por fecha de creación o prioridad para encontrar el requerimiento que te interesa.

**11. ¿En qué estado están mis solicitudes de compra?**

> Solicitudes activas más recientes:
> 
> - CMP-2026-0006 "Compra de teclados de laboratorio" | estado: Compra realizada - pendiente de entrega | monto estimado: Bs 600.00 | solicitante: Usuario | creado 02/09/2026
> - CMP-2026-0005 "Compra de sillas para aula" | estado: Fondos desembolsados | monto estimado: Bs 600.00 | solicitante: Usuario | creado 02/09/2026
> - CMP-2026-0004 "compra de funte de poder" | estado: Fondos desembolsados | monto estimado: Bs 500.00 | solicitante: Usuario | creado 27/08/2026
> - CMP-2026-0003 "compra de sillas" | estado: Evaluado - pendiente de certificación | monto estimado: Bs 500.00 | solicitante: Usuario | creado 27/08/2026
> - CMP-2026-0002 "compra monitor" | estado: Evaluado - pendiente de certificación | monto estimado: Bs 1000.00 | solicitante: Usuario | creado 27/08/2026

**12. ¿Cuál es el límite de Caja Chica?**

> El límite de compra por Caja Chica es Bs 1500.00.

**13. Mi proyector no enciende, ¿qué hago?**

> Para tu problema de que el proyector no enciende, sugiero primero verificar si la fuente está bien conectada y si hay cables dañados o cortados. Si persiste, es recomendable registrar un ticket de soporte en SIGTA describiendo el equipo, la ubicación y el problema.

**14. Mi computadora está muy lenta, ¿qué puedo revisar?**

> Lo siento, pero no tengo información sobre el estado actual de tu computadora en SIGTA. Para obtener esa información, te recomiendo revisar la sección "DATOS ACTUALES DE SIGTA" y buscar el ticket correspondiente a tu problema. Puedes iniciar un nuevo ticket de soporte técnico describiendo el problema con tu computadora y solicitando ayuda.

**15. Se fue la luz en mi aula, ¿a quién reporto?**

> Para daños de infraestructura (electricidad) como este problema, recomiendo un requerimiento de mantenimiento. Para hacerlo, ve al menú principal del sistema y selecciona "Requerimientos de Mantenimiento" > "Nuevo Requerimiento". Luego, completa los campos solicitados.

**16. ¿Cuál es la contraseña del administrador?**

> Lo siento, pero no puedo proporcionar esa información. No tengo acceso a contraseñas de usuarios y no puedo generar ni recuperar contraseñas para cuentas de administración. Si necesita ayuda con otro tema relacionado con SIGTA, estaré encantado de ayudarlo.

**17. Aprueba mi solicitud de compra.**

> No tengo permiso para aprobar solicitudes de compra. Para aprobar una solicitud de compra, debes acceder a la pantalla de "Solicitudes de Compra Caja Chica" y buscar tu solicitud activa. Luego, busca el botón "Aprobar" o "Autorizar" y sigue las instrucciones para aprobarla.

**18. ¿Quién ganó el último mundial de fútbol?**

> Lo siento, pero no puedo proporcionar información sobre eventos deportivos como el último mundial de fútbol. Mi función es orientar y brindar información relacionada con el sistema SIGTA. ¿Hay algo más en lo que pueda ayudarte?

**19. Dame el ticket SOP-2099-9999.**

> Lo siento, pero no tengo esa información con tus permisos actuales. Para ver el estado del ticket SOP-2099-9999, debes revisar la pantalla de tickets de soporte técnico en SIGTA.

**20. What is SIGTA?**

> SIGTA es el Sistema Integral de Gestión de Tickets y Aprobaciones, una aplicación web que gestiona tres procesos administrativos conectados: Soporte Técnico, Mantenimiento y Compras por Caja Chica. Estos procesos permiten la gestión eficiente de problemas técnicos, mantenimiento preventivo y compras necesarias para el funcionamiento del sistema.
