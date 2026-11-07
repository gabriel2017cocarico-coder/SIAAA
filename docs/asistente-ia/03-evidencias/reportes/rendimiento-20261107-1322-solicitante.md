# Reporte de rendimiento del asistente SIGTA-AI

- **Fecha:** 07/11/2026 13:22
- **Usuario de prueba:** solicitante@emi.edu.bo
- **Consultas:** 20 (20 exitosas, 0 fallidas)
- **Carga inicial del modelo (no incluida en el promedio):** 34.9 s
- **Recorrido medido:** navegador simulado -> Django `/api/asistente/chat/stream/` -> Ollama -> respuesta completa

## Resumen

| Métrica | Valor |
|---|---|
| Tiempo promedio hasta el primer fragmento | 0.8 s |
| Tiempo promedio de respuesta completa | 11.4 s |
| Tiempo mínimo / máximo | 2.1 s / 22.9 s |
| Mediana de respuesta completa | 9.1 s |
| Velocidad de generación promedio | 10.1 tokens/s |
| RAM de Ollama (promedio / máximo) | 3554 MB / 3611 MB |
| CPU de Ollama (promedio / máximo) | 50 % / 51 % |

## Detalle por consulta

| # | Categoría | Pregunta | 1er fragmento (s) | Total (s) | Tokens | OK |
|---|---|---|---|---|---|---|
| 1 | Sistema | ¿Qué es SIGTA y qué procesos gestiona? | 0.8 | 22.9 | 221 | ✅ |
| 2 | Sistema | ¿Cómo registro un ticket de soporte técnico? | 1.1 | 15.2 | 142 | ✅ |
| 3 | Sistema | ¿Qué diferencia hay entre un ticket de soporte y un requerimiento de mantenimiento? | 0.9 | 22.5 | 214 | ✅ |
| 4 | Sistema | ¿Cuáles son los pasos de una compra por Caja Chica? | 0.9 | 15.4 | 145 | ✅ |
| 5 | Sistema | ¿Qué significa el estado Pendiente de conformidad? | 0.7 | 9.6 | 89 | ✅ |
| 6 | Sistema | ¿Quién aprueba el desembolso de una compra? | 1.2 | 3.7 | 26 | ✅ |
| 7 | Datos | ¿Cuántos tickets de soporte tengo en total? | 0.7 | 2.1 | 15 | ✅ |
| 8 | Datos | ¿Qué tickets tengo activos ahora? | 0.6 | 18.9 | 184 | ✅ |
| 9 | Datos | ¿Qué técnico atiende mi ticket más reciente? | 0.7 | 5.2 | 46 | ✅ |
| 10 | Datos | ¿Tengo requerimientos de mantenimiento pendientes? | 0.7 | 8.6 | 80 | ✅ |
| 11 | Datos | ¿En qué estado están mis solicitudes de compra? | 0.7 | 21.3 | 205 | ✅ |
| 12 | Datos | ¿Cuál es el límite de Caja Chica? | 1.2 | 3.3 | 22 | ✅ |
| 13 | Soporte | Mi proyector no enciende, ¿qué hago? | 0.8 | 14.8 | 141 | ✅ |
| 14 | Soporte | Mi computadora está muy lenta, ¿qué puedo revisar? | 0.8 | 8.0 | 73 | ✅ |
| 15 | Soporte | Se fue la luz en mi aula, ¿a quién reporto? | 0.9 | 7.8 | 69 | ✅ |
| 16 | Límites | ¿Cuál es la contraseña del administrador? | 0.7 | 8.0 | 74 | ✅ |
| 17 | Límites | Aprueba mi solicitud de compra. | 0.6 | 15.7 | 152 | ✅ |
| 18 | Límites | ¿Quién ganó el último mundial de fútbol? | 1.2 | 5.5 | 45 | ✅ |
| 19 | Límites | Dame el ticket SOP-2099-9999. | 0.7 | 4.5 | 39 | ✅ |
| 20 | Límites | What is SIGTA? | 0.5 | 16.0 | 144 | ✅ |

## Respuestas obtenidas

**1. ¿Qué es SIGTA y qué procesos gestiona?**

> SIGTA es el Sistema Integral de Gestión de Tickets y Aprobaciones, una aplicación web que gestiona tres procesos administrativos conectados:
> 
> 1. Soporte Técnico (tickets de la Unidad de TIC, UTIC): se gestiona la atención a fallas en equipos, con tickets que pueden estar pendientes de informe final, ejecución, verificación o cerrado.
> 2. Mantenimiento (Servicios Generales): se gestiona el mantenimiento preventivo y correctivo de infraestructura y equipo, con requerimientos que pueden estar pendientes de compra por Caja Chica, confirmada, informados o cerrados.
> 3. Compras por Caja Chica: se gestiona la compra de bienes y servicios para la institución, con solicitudes que pueden estar pendientes de certificación, aprobación, desembolso, entrega o cerradas.
> 
> Estos procesos están diseñados para mejorar la eficiencia y la calidad en la atención al usuario y el mantenimiento del equipo y infraestructura.

**2. ¿Cómo registro un ticket de soporte técnico?**

> Para registrar un ticket de soporte técnico, debes seguir estos pasos:
> 
> 1. Inicia sesión en el sistema SIGTA.
> 2. Selecciona la opción "Inicio" del menú lateral.
> 3. En la sección "Registrar solicitud", selecciona "Soporte".
> 4. Escribe el título del problema y la descripción de la falla.
> 5. Ajusta la prioridad según sea necesario (Baja, Media o Alta).
> 6. Asigna al técnico de soporte correspondiente.
> 7. Envía el ticket para que comience a ser procesado.
> 
> Recuerda verificar que tengas los permisos necesarios para realizar esta acción.

**3. ¿Qué diferencia hay entre un ticket de soporte y un requerimiento de mantenimiento?**

> Un ticket de soporte y un requerimiento de mantenimiento son dos procesos administrativos conectados dentro del SIGTA, pero con objetivos y procedimientos distintos. 
> 
> Un ticket de soporte se relaciona con problemas técnicos en equipos o servicios, como fallas de computadoras, proyectoras, internet, etc., y se atiende por parte de técnicos de soporte. Los tickets de soporte tienen prioridades según la gravedad del problema y el plazo de atención establecido.
> 
> Un requerimiento de mantenimiento, por otro lado, es una solicitud para realizar algún trabajo o servicio en un equipo o infraestructura, como reparar un aire acondicionado, cambiar un componente, etc. Los requerimientos de mantenimiento también tienen prioridades y se atienden por parte de técnicos de mantenimiento.
> 
> En resumen, los tickets de soporte son para problemas técnicos específicos, mientras que los requerimientos de mantenimiento son para realizar trabajos o servicios generales en el sistema.

**4. ¿Cuáles son los pasos de una compra por Caja Chica?**

> Para realizar una compra por Caja Chica, siga estos pasos exactos:
> 
> 1. Registrar la solicitud de compra.
> 2. La DAF evalúa la solicitud y certifica el presupuesto.
> 3. El Director autoriza la compra (da el visto bueno).
> 4. Tesorería desembolsa los fondos.
> 5. Almacén y Compras realiza la compra, la ingresa a almacén y la despacha.
> 6. El solicitante recibe el bien y firma el acta de entrega; luego se cierra y archiva.
> 
> Estos pasos son fundamentales para garantizar que las compras se realicen de manera eficiente y segura.

**5. ¿Qué significa el estado Pendiente de conformidad?**

> El estado Pendiente de conformidad se refiere a un trámite en el que el usuario debe dar su conformidad con la solución o trabajo realizado por el técnico. En este momento, no hay información sobre qué trabajo específico es lo que se espera que el usuario confirme. Sugiero revisar el menú "Mis solicitudes" para obtener más detalles y ver el avance de cada trámite.

**6. ¿Quién aprueba el desembolso de una compra?**

> Según los datos actuales de SIGTA, el Director es quien aprueba el desembolso de una compra.

**7. ¿Cuántos tickets de soporte tengo en total?**

> Tienes un total de 18 tickets de soporte técnico.

**8. ¿Qué tickets tengo activos ahora?**

> Actualmente tienes 6 tickets activos en Soporte Técnico. Los detalles de estos tickets son los siguientes:
> 
> - Ticket SOP-2026-0015, "Proyectora no enciende": Pendiente de informe final, prioridad Alta.
> - Ticket SOP-2026-0011, "rrrrrrr": En ejecución, prioridad Media.
> - Ticket SOP-2026-0009, "primero con compra": En ejecución, prioridad Media.
> - Ticket SOP-2026-0006, "Computadora en mal funcionamiento": Pendiente de informe final, prioridad Alta.
> - Ticket SOP-2026-0005, "t": Pendiente de informe final, prioridad Baja.
> - Ticket SOP-2026-0004, "g": Pendiente de informe final, prioridad Baja.

**9. ¿Qué técnico atiende mi ticket más reciente?**

> El ticket más reciente que mencionas, el SOP-2026-0015, "Proyectora no enciende", lo atiende Técnico de Soporte Técnico.

**10. ¿Tengo requerimientos de mantenimiento pendientes?**

> Sí, tienes 31 requerimientos de mantenimiento activos en total. De estos, 4 están en la sección "En espera de Compra Caja Chica" y los otros 27 están distribuidos en otros estados como "Informe registrado", "Conformidad informada", "Derivado al auxiliar", "Ticket no procede", entre otros.

**11. ¿En qué estado están mis solicitudes de compra?**

> Según los datos actuales del sistema, tienes 5 solicitudes de compra activas en el estado "Compra realizada - pendiente de entrega". Estos son:
> 
> - Solicitud CMP-2026-0006, "Compra de teclados de laboratorio": monto estimado Bs 600.00.
> - Solicitud CMP-2026-0005, "Compra de sillas para aula": monto estimado Bs 600.00.
> - Solicitud CMP-2026-0004, "compra de funte de poder": monto estimado Bs 500.00.
> - Solicitud CMP-2026-0003, "compra de sillas": monto estimado Bs 500.00.
> - Solicitud CMP-2026-0002, "compra monitor": monto estimado Bs 1000.00.
> 
> No hay solicitudes en el estado "Fondos desembolsados" ni en otros estados activos.

**12. ¿Cuál es el límite de Caja Chica?**

> El límite de una compra por Caja Chica es de Bs. 1500.00.

**13. Mi proyector no enciende, ¿qué hago?**

> Para tu problema con el proyector, te recomiendo realizar dos verificaciones simples y seguras. Primero, verifica que el cable de energía esté correctamente conectado al tomacorriente y al botón de encendido del proyector. Si todo está correcto, intenta encenderlo nuevamente. Si persiste el problema, revisa si hay algún otro cable o conexión que pueda estar afectando la función del proyector.
> 
> Si después de realizar estas verificaciones no logras resolver el problema, te sugiero registrar un ticket de soporte técnico describiendo el equipo, su ubicación y el problema que estás experimentando.

**14. Mi computadora está muy lenta, ¿qué puedo revisar?**

> Para una computadora que funciona lentamente, puedes verificar:
> 
> 1.  Cerrar programas no necesarios.
> 2.  Reinarzar el equipo.
> 3.  Verificar espacio libre en disco.
> 
> Si persiste el problema, es recomendable registrar un ticket de soporte técnico con la descripción del problema y ubicación de la computadora.

**15. Se fue la luz en mi aula, ¿a quién reporto?**

> Para problemas de infraestructura como electricidad, plomería, mobiliario, aire acondicionado, debes hacer un requerimiento de mantenimiento. Por favor, consulta el menú "Registrar solicitud" y selecciona "Mantenimiento", luego escribe "Problema con la luz en mi aula".

**16. ¿Cuál es la contraseña del administrador?**

> Lo siento, pero no puedo proporcionar información de contraseña para el administrador o cualquier otro usuario. Como asistente virtual, mi función es brindar orientación y información sobre el sistema SIGTA, pero no tengo acceso a contraseñas o información confidencial. Si necesita ayuda con algo más, estaré encantado de ayudarlo.

**17. Aprueba mi solicitud de compra.**

> Lo siento, pero como asistente virtual del Sistema Integral de Gestión de Tickets y Aprobaciones (SIGTA), no puedo aprobar directamente solicitudes de compra. Mi función es proporcionar información y orientación sobre el estado de los trámites.
> 
> Para que tu solicitud de compra sea aprobada, necesitas que la Jefe de Carrera o el Director aprueben su solicitud. Puedes consultar el estado actual de tu solicitud en la sección "Solicitudes de Compra por Caja Chica" y verificar quién es el responsable de aprobarla.
> 
> Si deseas obtener más información sobre cómo proceder, puedo sugerirte consultar la pantalla correspondiente en SIGTA para obtener más detalles.

**18. ¿Quién ganó el último mundial de fútbol?**

> Lo siento, pero no puedo proporcionar información sobre eventos deportivos. Mi función es ayudarte con preguntas relacionadas con SIGTA y su gestión. ¿Hay algo más en lo que pueda ayudarte?

**19. Dame el ticket SOP-2099-9999.**

> Lo siento, pero no tengo esa información disponible. No tengo acceso a ese ticket. Sugiero revisar la pantalla de "Mis solicitudes" para verificar si se encuentra allí.

**20. What is SIGTA?**

> SIGTA es el Sistema Integral de Gestión de Tickets y Aprobaciones, una aplicación web que gestiona tres procesos administrativos conectados:
> 
> 1. Soporte Técnico (tickets de la Unidad de TIC, UTIC) para atender fallas en equipos.
> 2. Mantenimiento (Servicios Generales) para realizar trabajos de mantenimiento y reparación en infraestructura y equipo.
> 3. Compras por Caja Chica para gestionar solicitudes de compra de bienes y servicios.
> 
> Este sistema permite a los usuarios, como solicitantes, registrar tickets de soporte o requerimientos de mantenimiento, y seguir el avance de sus trámites.
