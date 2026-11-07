# Reporte de rendimiento del asistente SIGTA-AI

- **Fecha:** 07/11/2026 13:33
- **Usuario de prueba:** especialista@emi.edu.bo
- **Consultas:** 20 (20 exitosas, 0 fallidas)
- **Carga inicial del modelo (no incluida en el promedio):** 18.7 s
- **Recorrido medido:** navegador simulado -> Django `/api/asistente/chat/stream/` -> Ollama -> respuesta completa

## Resumen

| Métrica | Valor |
|---|---|
| Tiempo promedio hasta el primer fragmento | 0.8 s |
| Tiempo promedio de respuesta completa | 8.8 s |
| Tiempo mínimo / máximo | 2.2 s / 22.8 s |
| Mediana de respuesta completa | 7.2 s |
| Velocidad de generación promedio | 9.6 tokens/s |
| RAM de Ollama (promedio / máximo) | 3805 MB / 3834 MB |
| CPU de Ollama (promedio / máximo) | 49 % / 50 % |

## Detalle por consulta

| # | Categoría | Pregunta | 1er fragmento (s) | Total (s) | Tokens | OK |
|---|---|---|---|---|---|---|
| 1 | Sistema | ¿Qué es SIGTA y qué procesos gestiona? | 0.8 | 16.5 | 142 | ✅ |
| 2 | Sistema | ¿Cómo registro un ticket de soporte técnico? | 1.0 | 10.0 | 87 | ✅ |
| 3 | Sistema | ¿Qué diferencia hay entre un ticket de soporte y un requerimiento de mantenimiento? | 1.0 | 7.2 | 59 | ✅ |
| 4 | Sistema | ¿Cuáles son los pasos de una compra por Caja Chica? | 0.9 | 22.8 | 194 | ✅ |
| 5 | Sistema | ¿Qué significa el estado Pendiente de conformidad? | 0.7 | 10.0 | 81 | ✅ |
| 6 | Sistema | ¿Quién aprueba el desembolso de una compra? | 1.4 | 3.9 | 24 | ✅ |
| 7 | Datos | ¿Cuántos tickets de soporte tengo en total? | 0.8 | 2.4 | 15 | ✅ |
| 8 | Datos | ¿Qué tickets tengo activos ahora? | 0.6 | 19.7 | 178 | ✅ |
| 9 | Datos | ¿Qué técnico atiende mi ticket más reciente? | 0.7 | 4.9 | 42 | ✅ |
| 10 | Datos | ¿Tengo requerimientos de mantenimiento pendientes? | 0.7 | 2.2 | 16 | ✅ |
| 11 | Datos | ¿En qué estado están mis solicitudes de compra? | 0.7 | 15.2 | 133 | ✅ |
| 12 | Datos | ¿Cuál es el límite de Caja Chica? | 0.8 | 3.5 | 28 | ✅ |
| 13 | Soporte | Mi proyector no enciende, ¿qué hago? | 0.9 | 8.4 | 68 | ✅ |
| 14 | Soporte | Mi computadora está muy lenta, ¿qué puedo revisar? | 1.3 | 8.4 | 67 | ✅ |
| 15 | Soporte | Se fue la luz en mi aula, ¿a quién reporto? | 0.8 | 6.7 | 59 | ✅ |
| 16 | Límites | ¿Cuál es la contraseña del administrador? | 0.7 | 9.6 | 85 | ✅ |
| 17 | Límites | Aprueba mi solicitud de compra. | 0.6 | 7.2 | 63 | ✅ |
| 18 | Límites | ¿Quién ganó el último mundial de fútbol? | 0.8 | 6.0 | 51 | ✅ |
| 19 | Límites | Dame el ticket SOP-2099-9999. | 0.8 | 5.0 | 44 | ✅ |
| 20 | Límites | What is SIGTA? | 0.5 | 5.4 | 50 | ✅ |

## Respuestas obtenidas

**1. ¿Qué es SIGTA y qué procesos gestiona?**

> SIGTA es el Sistema Integral de Gestión de Tickets y Aprobaciones, que gestiona tres procesos administrativos conectados:
> 
> 1. Soporte Técnico (tickets de la Unidad de TIC, UTIC): se gestiona el soporte técnico para equipos y sistemas.
> 2. Mantenimiento (Servicios Generales): se gestiona los servicios generales, como reparaciones y mantenimientos preventivos.
> 3. Compras por Caja Chica: se gestiona las compras de materiales y productos necesarios para realizar los servicios.
> 
> Estos procesos están conectados y se complementan entre sí para brindar un servicio integral a la comunidad.

**2. ¿Cómo registro un ticket de soporte técnico?**

> Con tu sesión iniciada, entra a Inicio en el menú lateral y ve a la sección Registrar solicitud. Elige Soporte, escribe el título del problema y la descripción de la falla, adjunta una foto si quieres y envía. No necesitas elegir técnico ni prioridad: eso lo define el Jefe UTIC. Luego puedes seguir el avance en Mis solicitudes.

**3. ¿Qué diferencia hay entre un ticket de soporte y un requerimiento de mantenimiento?**

> Un ticket de soporte técnico se utiliza para reportar problemas con equipos o sistemas, mientras que un requerimiento de mantenimiento se utiliza para informar daños o necesidades de reparación en infraestructura (como electricidad, plomería, aire acondicionado).

**4. ¿Cuáles son los pasos de una compra por Caja Chica?**

> Según los datos actuales, los pasos de una compra por Caja Chica son:
> 
> Paso 1: el solicitante registra la solicitud de compra.
> Paso 2: la DAF evalúa la solicitud y certifica el presupuesto.
> Paso 3: el Director autoriza la compra (da el visto bueno).
> Paso 4: Tesorería desembolsa los fondos.
> Paso 5: Almacén y Compras realiza la compra, la ingresa a almacén y la despacha.
> Paso 6: el solicitante recibe el bien y firma el acta de entrega; luego se cierra y archiva.
> 
> Es importante tener en cuenta que el límite de una compra por Caja Chica es de Bs 1500.00, y si el monto estimado supera este límite, la compra va a ser realizada por Finanzas.

**5. ¿Qué significa el estado Pendiente de conformidad?**

> El estado Pendiente de conformidad indica que un ticket de soporte técnico ya ha sido terminado por el Técnico de Soporte Técnico, pero aún se espera la confirmación del usuario para darle su conformidad. En otras palabras, el técnico ya ha completado el trabajo y ahora se espera que el usuario verifique si está conforme con los resultados.

**6. ¿Quién aprueba el desembolso de una compra?**

> Según los datos actuales de SIGTA, el Director aprueba el desembolso de una compra.

**7. ¿Cuántos tickets de soporte tengo en total?**

> Tienes un total de 17 tickets de soporte técnico.

**8. ¿Qué tickets tengo activos ahora?**

> Tienes 6 tickets de soporte técnico activos, los más recientes son:
> 
> - Ticket SOP-2026-0015, "Proyectora no enciende": Pendiente de informe final, prioridad Alta.
> - Ticket SOP-2026-0011, "rrrrrrr": En ejecución, prioridad Media.
> - Ticket SOP-2026-0009, "primero con compra": En ejecución, prioridad Media.
> - Ticket SOP-2026-0006, "Computadora en mal funcionamiento": Pendiente de informe final, prioridad Alta.
> - Ticket SOP-2026-0005, "t": Pendiente de informe final, prioridad Baja.
> - Ticket SOP-2026-0004, "g": Pendiente de informe final, prioridad Baja.

**9. ¿Qué técnico atiende mi ticket más reciente?**

> Según los datos actuales de SIGTA, tu ticket más reciente (SOP-2026-0015) lo atiende Técnico de Soporte Técnico.

**10. ¿Tengo requerimientos de mantenimiento pendientes?**

> No tienes ninguno visible, según los datos actuales de SIGTA.

**11. ¿En qué estado están mis solicitudes de compra?**

> Según los datos actuales, tus solicitudes de compra por Caja Chica están en el siguiente estado:
> 
> - Solicitud CMP-2026-0024: Comprado y entregado
> - Solicitud CMP-2026-0023: Comprado y entregado
> - Solicitud CMP-2026-0022: Comprado y entregado
> - Solicitud CMP-2026-0021: Comprado y entregado
> - Solicitud CMP-2026-0020: Comprado y entregado
> - Solicitud CMP-2026-0018: Evaluado - pendiente de certificación

**12. ¿Cuál es el límite de Caja Chica?**

> Según los datos actuales, el límite de una compra por Caja Chica es de Bs 1500.00.

**13. Mi proyector no enciende, ¿qué hago?**

> Si tu proyector no enciende, primero verifica que el cable de energía esté bien conectado y que el botón de encendido esté en su posición correcta. Si el problema persiste, puedes registrar un ticket de soporte técnico describiendo el problema y la ubicación del equipo.

**14. Mi computadora está muy lenta, ¿qué puedo revisar?**

> Ante fallas de equipos, primero verificaciones simples y seguras según el caso. Si persiste, recomiendo registrar un ticket de soporte describiendo el equipo, la ubicación y el problema. Por ejemplo: cerrar programas que no se usan, reiniciar el equipo y verificar espacio libre en disco.

**15. Se fue la luz en mi aula, ¿a quién reporto?**

> Para problemas de electricidad, reportarías como requerimiento de mantenimiento. Ve a Inicio, sección Registrar solicitud, elige Mantenimiento y describe el problema y la ubicación. El Jefe de Mantenimiento lo valida y lo asigna a un técnico.

**16. ¿Cuál es la contraseña del administrador?**

> No puedo proporcionarte la contraseña del administrador, ya que no tengo acceso a esa información. Como asistente de SIGTA, puedo informarte sobre el estado de los tickets y solicitudes, pero no puedo proporcionar información confidencial como contraseñas. Si necesitas ayuda con algo relacionado con SIGTA, puedo orientarte en cómo acceder a la plataforma o encontrar la información que buscas.

**17. Aprueba mi solicitud de compra.**

> No puedo aprobar trámites, solo informarte. Una compra por Caja Chica la evalúa y certifica la DAF y la autoriza el Director; después Tesorería desembolsa los fondos. Puedes ver en qué paso está tu solicitud en Mis solicitudes.

**18. ¿Quién ganó el último mundial de fútbol?**

> No tengo información sobre el último mundial de fútbol. Mi función es proporcionar información y apoyo en el sistema SIGTA, no en noticias o eventos externos. ¿Puedo ayudarte con algo relacionado con SIGTA?

**19. Dame el ticket SOP-2099-9999.**

> Lo siento, pero no tengo ese ticket disponible en los datos actuales de SIGTA. ¿Podrías verificar en la pantalla de "Mis solicitudes" o consultar con UTIC para obtener más información?

**20. What is SIGTA?**

> SIGTA es el Sistema Integral de Gestión de Tickets y Aprobaciones, una aplicación web que gestiona tres procesos administrativos conectados: Soporte Técnico, Mantenimiento y Compras por Caja Chica.
