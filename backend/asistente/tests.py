"""
Pruebas del módulo asistente.

Ollama se simula con unittest.mock: las pruebas no necesitan el
motor de IA encendido y verifican que el backend nunca responda
con un error 500 ante sus fallas.

Ejecutar:  python manage.py test asistente
"""

from unittest import mock

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from usuarios.models import Usuario

from . import servicios


@override_settings(OLLAMA_MODELO='sigta-ai')
class ChatAsistenteTests(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='prueba.asistente',
            email='prueba.asistente@emi.edu.bo',
            password='Clave-Segura-123*',
            nombre_completo='Usuario de Prueba',
        )
        self.cliente = APIClient()
        self.cliente.force_authenticate(self.usuario)

    # ---------- seguridad y validación ----------

    def test_sin_sesion_responde_401(self):
        respuesta = APIClient().post('/api/asistente/chat/', {'mensaje': 'hola'}, format='json')
        self.assertEqual(respuesta.status_code, 401)

    def test_mensaje_vacio_responde_400(self):
        respuesta = self.cliente.post('/api/asistente/chat/', {'mensaje': '   '}, format='json')
        self.assertEqual(respuesta.status_code, 400)
        self.assertFalse(respuesta.json()['ok'])

    def test_mensaje_demasiado_largo_responde_400(self):
        respuesta = self.cliente.post('/api/asistente/chat/', {'mensaje': 'a' * 1001}, format='json')
        self.assertEqual(respuesta.status_code, 400)

    # ---------- respuesta correcta ----------

    @mock.patch('asistente.views.servicios.generar')
    def test_respuesta_correcta_en_json(self, generar):
        generar.return_value = {'texto': 'Hola, soy SIGTA-AI.', 'metricas': {'total_ms': 1200}}
        respuesta = self.cliente.post('/api/asistente/chat/', {'mensaje': '¿Qué es SIGTA?'}, format='json')

        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertTrue(datos['ok'])
        self.assertEqual(datos['respuesta'], 'Hola, soy SIGTA-AI.')
        self.assertEqual(datos['modelo'], 'sigta-ai')
        self.assertIn('duracion_ms', datos)

        prompt = generar.call_args[0][0]
        self.assertIn('¿Qué es SIGTA?', prompt)
        self.assertIn('DATOS ACTUALES DE SIGTA', prompt)
        self.assertIn('Usuario de Prueba', prompt)

    # ---------- fallas de Ollama: nunca 500 ----------

    def _falla(self, excepcion, codigo):
        with mock.patch('asistente.views.servicios.generar', side_effect=excepcion('detalle')):
            respuesta = self.cliente.post('/api/asistente/chat/', {'mensaje': 'hola'}, format='json')
        self.assertEqual(respuesta.status_code, codigo)
        self.assertFalse(respuesta.json()['ok'])
        self.assertTrue(respuesta.json()['error'])

    def test_ollama_apagado_responde_503(self):
        self._falla(servicios.OllamaNoDisponible, 503)

    def test_ollama_lento_responde_504(self):
        self._falla(servicios.OllamaTiempoAgotado, 504)

    def test_modelo_no_instalado_responde_503(self):
        self._falla(servicios.ModeloNoEncontrado, 503)

    @override_settings(OLLAMA_URL='http://127.0.0.1:9')
    def test_conexion_real_rechazada_responde_503(self):
        # Puerto 9 (discard): nadie escucha, la conexión es rechazada.
        respuesta = self.cliente.post('/api/asistente/chat/', {'mensaje': 'hola'}, format='json')
        self.assertEqual(respuesta.status_code, 503)

    @override_settings(OLLAMA_URL='http://127.0.0.1:9')
    def test_stream_con_ollama_apagado_responde_503(self):
        respuesta = self.cliente.post('/api/asistente/chat/stream/', {'mensaje': 'hola'}, format='json')
        self.assertEqual(respuesta.status_code, 503)

    @override_settings(OLLAMA_URL='http://127.0.0.1:9')
    def test_estado_con_ollama_apagado(self):
        respuesta = self.cliente.get('/api/asistente/estado/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.json()['ollama'])

    # ---------- streaming ----------

    def test_stream_entrega_fragmentos(self):
        def falso_stream(_prompt):
            yield {'texto': 'Hola, '}
            yield {'texto': 'Paola.'}
            yield {'fin': True, 'metricas': {}}

        with mock.patch('asistente.views.servicios.generar_stream', side_effect=falso_stream):
            respuesta = self.cliente.post('/api/asistente/chat/stream/', {'mensaje': 'hola'}, format='json')
            cuerpo = b''.join(respuesta.streaming_content).decode('utf-8')

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('"texto": "Hola, "', cuerpo)
        self.assertIn('"fin": true', cuerpo)


class PrivacidadContextoTests(TestCase):
    """El contexto solo debe incluir lo que el usuario puede ver."""

    def test_usuario_sin_tramites_no_ve_tramites_ajenos(self):
        from rest_framework.request import Request
        from rest_framework.test import APIRequestFactory

        from .contexto import construir_contexto

        usuario = Usuario.objects.create_user(
            username='nuevo', email='nuevo@emi.edu.bo', password='Clave-Segura-123*',
            nombre_completo='Usuario Nuevo',
        )
        peticion = Request(APIRequestFactory().post('/api/asistente/chat/'))
        peticion._force_auth_user = usuario
        peticion._user = usuario

        contexto = construir_contexto(peticion)
        self.assertIn('Usuario Nuevo', contexto)
        self.assertIn('TICKETS DE SOPORTE TÉCNICO: no tienes ninguno visible', contexto)
        self.assertIn('ninguna visible', contexto)
