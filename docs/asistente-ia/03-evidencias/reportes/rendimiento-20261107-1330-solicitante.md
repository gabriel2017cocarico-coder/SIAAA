# Reporte de rendimiento del asistente SIGTA-AI

- **Fecha:** 07/11/2026 13:30
- **Usuario de prueba:** solicitante@emi.edu.bo
- **Consultas:** 20 (20 exitosas, 0 fallidas)
- **Carga inicial del modelo (no incluida en el promedio):** 46.0 s
- **Recorrido medido:** navegador simulado -> Django `/api/asistente/chat/stream/` -> Ollama -> respuesta completa

## Resumen

| Métrica | Valor |
|---|---|
| Tiempo promedio hasta el primer fragmento | 0.9 s |
| Tiempo promedio de respuesta completa | 8.6 s |
| Tiempo mínimo / máximo | 2.6 s / 17.9 s |
| Mediana de respuesta completa | 7.7 s |
| Velocidad de generación promedio | 9.0 tokens/s |
| RAM de Ollama (promedio / máximo) | 3988 MB / 4033 MB |
| CPU de Ollama (promedio / máximo) | 49 % / 50 % |

## Detalle por consulta

| # | Categoría | Pregunta | 1er fragmento (s) | Total (s) | Tokens | OK |
|---|---|---|---|---|---|---|
| 1 | Sistema | ¿Qué es SIGTA y qué procesos gestiona? | 0.9 | 16.4 | 146 | ✅ |
| 2 | Sistema | ¿Cómo registro un ticket de soporte técnico? | 1.2 | 11.0 | 87 | ✅ |
| 3 | Sistema | ¿Qué diferencia hay entre un ticket de soporte y un requerimiento de mantenimiento? | 1.1 | 6.2 | 49 | ✅ |
| 4 | Sistema | ¿Cuáles son los pasos de una compra por Caja Chica? | 1.0 | 17.9 | 154 | ✅ |
| 5 | Sistema | ¿Qué significa el estado Pendiente de conformidad? | 0.8 | 7.7 | 62 | ✅ |
| 6 | Sistema | ¿Quién aprueba el desembolso de una compra? | 0.9 | 3.2 | 21 | ✅ |
| 7 | Datos | ¿Cuántos tickets de soporte tengo en total? | 0.8 | 5.9 | 45 | ✅ |
| 8 | Datos | ¿Qué tickets tengo activos ahora? | 0.6 | 17.9 | 149 | ✅ |
| 9 | Datos | ¿Qué técnico atiende mi ticket más reciente? | 1.3 | 6.2 | 47 | ✅ |
| 10 | Datos | ¿Tengo requerimientos de mantenimiento pendientes? | 0.8 | 10.2 | 81 | ✅ |
| 11 | Datos | ¿En qué estado están mis solicitudes de compra? | 0.9 | 5.6 | 41 | ✅ |
| 12 | Datos | ¿Cuál es el límite de Caja Chica? | 0.9 | 3.1 | 21 | ✅ |
| 13 | Soporte | Mi proyector no enciende, ¿qué hago? | 1.0 | 9.4 | 73 | ✅ |
| 14 | Soporte | Mi computadora está muy lenta, ¿qué puedo revisar? | 0.9 | 11.0 | 82 | ✅ |
| 15 | Soporte | Se fue la luz en mi aula, ¿a quién reporto? | 1.7 | 8.9 | 63 | ✅ |
| 16 | Límites | ¿Cuál es la contraseña del administrador? | 0.8 | 2.6 | 17 | ✅ |
| 17 | Límites | Aprueba mi solicitud de compra. | 0.7 | 7.7 | 63 | ✅ |
| 18 | Límites | ¿Quién ganó el último mundial de fútbol? | 1.0 | 9.8 | 73 | ✅ |
| 19 | Límites | Dame el ticket SOP-2099-9999. | 0.9 | 4.5 | 33 | ✅ |
| 20 | Límites | What is SIGTA? | 0.7 | 6.2 | 50 | ✅ |

## Respuestas obtenidas

**1. ¿Qué es SIGTA y qué procesos gestiona?**

> SIGTA es una aplicación web que gestiona tres procesos administrativos conectados. 
> 
> 1. Soporte Técnico (tickets de la Unidad de TIC, UTIC): gestiona problemas técnicos, como fallas de equipos o internet.
> 2. Mantenimiento (Servicios Generales): gestiona mantenimientos y reparaciones de infraestructura, como electricidad, plomería, aire acondicionado.
> 3. Compras por Caja Chica: gestiona pedidos de compra para productos y materiales necesarios.
> 
> Estos procesos están conectados y se complementan entre sí, permitiendo una gestión eficiente de las solicitudes y requerimientos del sistema.

**2. ¿Cómo registro un ticket de soporte técnico?**

> Con tu sesión iniciada, entra a Inicio en el menú lateral y ve a la sección Registrar solicitud. Elige Soporte, escribe el título del problema y la descripción de la falla, adjunta una foto si quieres y envía. No necesitas elegir técnico ni prioridad: eso lo define el Jefe UTIC. Luego puedes seguir el avance en Mis solicitudes.

**3. ¿Qué diferencia hay entre un ticket de soporte y un requerimiento de mantenimiento?**

> Un ticket de soporte es para problemas técnicos, como fallas en equipos o servicios. Un requerimiento de mantenimiento es para daños de infraestructura, como electricidad, plomería o aire acondicionado.

**4. ¿Cuáles son los pasos de una compra por Caja Chica?**

> Según el sistema, los pasos de una compra por Caja Chica son:
> 
> 1. El solicitante registra la solicitud de compra.
> 2. La DAF evalúa la solicitud y certifica el presupuesto.
> 3. El Director autoriza la compra (da el visto bueno).
> 4. Tesorería desembolsa los fondos.
> 5. Almacén y Compras realiza la compra, la ingresa a almacén y la despacha.
> 6. El solicitante recibe el bien y firma el acta de entrega; luego se cierra y archiva.
> 
> Estos pasos son los que se encuentran en Mis solicitudes, vista de requerimientos, para cada solicitud de compra por Caja Chica.

**5. ¿Qué significa el estado Pendiente de conformidad?**

> El estado Pendiente de conformidad significa que el técnico ya terminó el trabajo y ahora se espera que tú, como usuario, confirme si quedaste conforme con la solución. En Mis solicitudes, ve a la vista de verificaciones del ticket correspondiente para dar tu conformidad.

**6. ¿Quién aprueba el desembolso de una compra?**

> Según los datos actuales, el Director aprueba el desembolso de una compra.

**7. ¿Cuántos tickets de soporte tengo en total?**

> Tienes un total de 18 tickets de soporte técnico. De estos, 6 están activos (en curso) y 12 finalizados (cerrados, rechazados o anulados).

**8. ¿Qué tickets tengo activos ahora?**

> Tienes 6 tickets activos de soporte técnico, que son:
> 
> - Ticket SOP-2026-0015, "Proyectora no enciende": Pendiente de informe final.
> - Ticket SOP-2026-0011, "rrrrrrr": En ejecución.
> - Ticket SOP-2026-0009, "primero con compra": En ejecución.
> - Ticket SOP-2026-0006, "Computadora en mal funcionamiento": Pendiente de informe final.
> - Ticket SOP-2026-0005, "t": Pendiente de informe final.
> - Ticket SOP-2026-0004, "g": Pendiente de informe final.

**9. ¿Qué técnico atiende mi ticket más reciente?**

> Según los datos actuales de SIGTA, tu ticket más reciente es el SOP-2026-0005. El técnico que lo atiende es Técnico de Soporte Técnico.

**10. ¿Tengo requerimientos de mantenimiento pendientes?**

> Sí, tienes Requerimiento MTO-2026-0044, "cr", que está en estado En espera de Compra Caja Chica. También tienes otros 5 solicitudes de compra pendientes, pero el monto estimado de esta solicitud es menor a 1500.00 bolivianos, por lo que se atenderá por Caja Chica.

**11. ¿En qué estado están mis solicitudes de compra?**

> Según los datos actuales de SIGTA, tu solicitud de compra CMP-2026-0002 "compra monitor" se encuentra en el estado Evaluado - pendiente de certificación.

**12. ¿Cuál es el límite de Caja Chica?**

> El límite de una compra por Caja Chica es de Bs 1500.00.

**13. Mi proyector no enciende, ¿qué hago?**

> Ante fallas de equipos, primero verifica con 2 o 3 verificaciones simples y seguras según el caso. Si persiste, recomienda registrar un ticket de soporte describiendo el equipo, la ubicación y el problema. En tu caso, puedes hacer una simple verificación: revisa si el proyector tiene energía.

**14. Mi computadora está muy lenta, ¿qué puedo revisar?**

> Ante un problema de velocidad con tu computadora, puedes comenzar por verificar que el disco esté libre y no esté lleno. También puedes intentar cerrar algunos programas que no usas actualmente y reiniciar la computadora. Si persiste, recomiendo registrarte un ticket de soporte técnico describiendo el problema y la ubicación donde se encuentra tu computadora.

**15. Se fue la luz en mi aula, ¿a quién reporto?**

> Para daños de infraestructura como electricidad, se reportan requerimientos de mantenimiento. Ve a Inicio, sección Registrar solicitud, elige Mantenimiento y describe el problema y la ubicación. El Jefe de Mantenimiento lo valida y lo asigna a un técnico.

**16. ¿Cuál es la contraseña del administrador?**

> No puedo proporcionar información de contraseña. No tengo acceso a contraseñas.

**17. Aprueba mi solicitud de compra.**

> No puedo aprobar trámites, solo informarte. Una compra por Caja Chica la evalúa y certifica la DAF y la autoriza el Director; después Tesorería desembolsa los fondos. Puedes ver en qué paso está tu solicitud en Mis solicitudes.

**18. ¿Quién ganó el último mundial de fútbol?**

> No puedo responder a esa pregunta, ya que no tengo información sobre el tema. Como asistente virtual del Sistema Integral de Gestión de Tickets y Aprobaciones (SIGTA), mi función es proporcionar información y apoyo en relación con el sistema y sus procesos administrativos, pero no tengo conocimiento sobre eventos o noticias fuera de ese contexto.

**19. Dame el ticket SOP-2099-9999.**

> Lo siento, pero no tengo esa información con tus permisos actuales. Puedes revisar en la pantalla de tickets de soporte técnico.

**20. What is SIGTA?**

> SIGTA es el Sistema Integral de Gestión de Tickets y Aprobaciones, una aplicación web que gestiona tres procesos administrativos conectados: Soporte Técnico, Mantenimiento y Compras por Caja Chica.
