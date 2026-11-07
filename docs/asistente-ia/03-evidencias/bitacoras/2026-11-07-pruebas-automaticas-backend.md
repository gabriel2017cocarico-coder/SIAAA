# Pruebas automáticas del módulo asistente

- **Fecha:** 07/11/2026 12:50
- **Comando:** `python manage.py test asistente`
- **Ollama:** simulado (mock) y conexión real rechazada (puerto 9), para probar las fallas
- **Resultado:** Ran 12 tests in 6.703s OK

| # | Prueba | Qué verifica | Resultado |
|---|---|---|---|
| 1 | `test_sin_sesion_responde_401` | sin sesion responde 401 | ✅ OK |
| 2 | `test_mensaje_vacio_responde_400` | mensaje vacio responde 400 | ✅ OK |
| 3 | `test_mensaje_demasiado_largo_responde_400` | mensaje demasiado largo responde 400 | ✅ OK |
| 4 | `test_respuesta_correcta_en_json` | respuesta correcta en json | ✅ OK |
| 5 | `test_ollama_apagado_responde_503` | ollama apagado responde 503 | ✅ OK |
| 6 | `test_ollama_lento_responde_504` | ollama lento responde 504 | ✅ OK |
| 7 | `test_modelo_no_instalado_responde_503` | modelo no instalado responde 503 | ✅ OK |
| 8 | `test_conexion_real_rechazada_responde_503` | conexion real rechazada responde 503 | ✅ OK |
| 9 | `test_stream_con_ollama_apagado_responde_503` | stream con ollama apagado responde 503 | ✅ OK |
| 10 | `test_estado_con_ollama_apagado` | estado con ollama apagado | ✅ OK |
| 11 | `test_stream_entrega_fragmentos` | stream entrega fragmentos | ✅ OK |
| 12 | `test_usuario_sin_tramites_no_ve_tramites_ajenos` | usuario sin tramites no ve tramites ajenos | ✅ OK |
