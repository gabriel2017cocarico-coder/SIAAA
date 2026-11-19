from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from .consultas import ConsultasConversacionales


class RegistrosSimulados:
    def __init__(self, objetos):
        self.objetos = objetos

    def filter(self, **filtros):
        nombre, valor = next(iter(filtros.items()))
        if nombre == "codigo__iexact":
            objetos = [obj for obj in self.objetos if obj.codigo.casefold() == valor.casefold()]
        elif nombre == "estado__codigo__in":
            objetos = [obj for obj in self.objetos if obj.estado.codigo in valor]
        else:
            objetos = [obj for obj in self.objetos if obj.codigo.casefold().endswith(valor.casefold())]
        return RegistrosSimulados(objetos)

    def first(self):
        return self.objetos[0] if self.objetos else None

    def count(self):
        return len(self.objetos)


class ConsultasConversacionalesTests(SimpleTestCase):
    def setUp(self):
        self.consultas = ConsultasConversacionales(usuario=object())
        self.solicitud = SimpleNamespace(
            codigo="MTO-2026-0050",
            titulo="Lluvia de chocolate",
            descripcion="Empezó el fenómeno del niño y comenzó a llover chocolate.",
            estado=SimpleNamespace(codigo="RECIBIDO", nombre="Recibido"),
            ubicacion="Pasillo central",
        )

    def test_resumen_y_estado_por_numero_parcial_de_solicitud(self):
        with (
            patch.object(self.consultas, "_tickets", return_value=RegistrosSimulados([])),
            patch.object(self.consultas, "_mantenimientos", return_value=RegistrosSimulados([self.solicitud])),
        ):
            respuesta = self.consultas.buscar(
                "Dame un resumen y condición de la solicitud de mantenimiento 0050"
            )

        self.assertIn("MTO-2026-0050", respuesta)
        self.assertIn("Resumen: Empezó el fenómeno del niño", respuesta)
        self.assertIn("Estado actual: Recibido", respuesta)
        self.assertIn("Ubicación: Pasillo central", respuesta)

    def test_resuelve_codigo_completo_sin_confiar_en_los_ultimos_registros(self):
        with (
            patch.object(self.consultas, "_tickets", return_value=RegistrosSimulados([])),
            patch.object(self.consultas, "_mantenimientos", return_value=RegistrosSimulados([self.solicitud])),
        ):
            respuesta = self.consultas.buscar(
                "¿Cuál es la condición de MTO-2026-0050?"
            )

        self.assertIn("Estado actual: Recibido", respuesta)

    def test_identificador_que_no_pertenece_a_sus_registros_no_inventa_datos(self):
        with (
            patch.object(self.consultas, "_tickets", return_value=RegistrosSimulados([])),
            patch.object(self.consultas, "_mantenimientos", return_value=RegistrosSimulados([])),
        ):
            respuesta = self.consultas.buscar("Dame el resumen de mantenimiento 0050")

        self.assertEqual(respuesta, "No encontré una solicitud tuya con el código o número 0050.")

    def test_cuenta_solo_solicitudes_cuyo_estado_indica_trabajo_en_curso(self):
        ticket = SimpleNamespace(estado=SimpleNamespace(codigo="EN_PROCESO"))
        mantenimiento = SimpleNamespace(estado=SimpleNamespace(codigo="EN_MANTENIMIENTO"))
        finalizado = SimpleNamespace(estado=SimpleNamespace(codigo="FINALIZADO"))
        with (
            patch.object(self.consultas, "_tickets", return_value=RegistrosSimulados([ticket])),
            patch.object(
                self.consultas,
                "_mantenimientos",
                return_value=RegistrosSimulados([mantenimiento, finalizado]),
            ),
        ):
            respuesta = self.consultas.buscar("¿Cuántas solicitudes tengo en proceso?")

        self.assertEqual(
            respuesta,
            "Tienes 2 solicitud(es) en proceso: 1 de soporte y 1 de mantenimiento.",
        )
