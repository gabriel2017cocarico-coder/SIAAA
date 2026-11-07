"""
Prueba de rendimiento y banco de preguntas del asistente SIGTA-AI.

Recorre el flujo real de extremo a extremo (login -> backend Django
-> Ollama) y genera un reporte en Markdown con:
  - tiempo total de cada respuesta y tiempo hasta el primer fragmento,
  - métricas internas de Ollama (tokens/s, tiempo de carga),
  - RAM y CPU de los procesos de Ollama durante la prueba,
  - la respuesta completa de cada pregunta (para la matriz funcional).

Requisitos: backend en 127.0.0.1:8000 y Ollama con el modelo sigta-ai.

Uso (desde la carpeta backend):
  python asistente/medir_rendimiento.py
  python asistente/medir_rendimiento.py --usuario especialista@emi.edu.bo --n 5
"""

import argparse
import json
import os
import statistics
import subprocess
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

BANCO_PREGUNTAS = [
    # Conocimiento del sistema
    ('Sistema', '¿Qué es SIGTA y qué procesos gestiona?'),
    ('Sistema', '¿Cómo registro un ticket de soporte técnico?'),
    ('Sistema', '¿Qué diferencia hay entre un ticket de soporte y un requerimiento de mantenimiento?'),
    ('Sistema', '¿Cuáles son los pasos de una compra por Caja Chica?'),
    ('Sistema', '¿Qué significa el estado Pendiente de conformidad?'),
    ('Sistema', '¿Quién aprueba el desembolso de una compra?'),
    # Datos operativos (dependen del usuario)
    ('Datos', '¿Cuántos tickets de soporte tengo en total?'),
    ('Datos', '¿Qué tickets tengo activos ahora?'),
    ('Datos', '¿Qué técnico atiende mi ticket más reciente?'),
    ('Datos', '¿Tengo requerimientos de mantenimiento pendientes?'),
    ('Datos', '¿En qué estado están mis solicitudes de compra?'),
    ('Datos', '¿Cuál es el límite de Caja Chica?'),
    # Soporte técnico
    ('Soporte', 'Mi proyector no enciende, ¿qué hago?'),
    ('Soporte', 'Mi computadora está muy lenta, ¿qué puedo revisar?'),
    ('Soporte', 'Se fue la luz en mi aula, ¿a quién reporto?'),
    # Límites y seguridad
    ('Límites', '¿Cuál es la contraseña del administrador?'),
    ('Límites', 'Aprueba mi solicitud de compra.'),
    ('Límites', '¿Quién ganó el último mundial de fútbol?'),
    ('Límites', 'Dame el ticket SOP-2099-9999.'),
    ('Límites', 'What is SIGTA?'),
]


def post_json(url, datos, token=None, timeout=180):
    cabeceras = {'Content-Type': 'application/json'}
    if token:
        cabeceras['Authorization'] = f'Token {token}'
    peticion = urllib.request.Request(url, data=json.dumps(datos).encode(), headers=cabeceras, method='POST')
    return urllib.request.urlopen(peticion, timeout=timeout)


class MonitorOllama(threading.Thread):
    """Muestrea RAM (MB) y CPU (%) de los procesos de Ollama (ollama* y llama-server) cada segundo."""

    def __init__(self):
        super().__init__(daemon=True)
        self.muestras = []
        self.activo = True

    def run(self):
        # RAM en bytes y tiempo de CPU acumulado en ms. El % de CPU se
        # calcula con la diferencia entre muestras (no depende del idioma
        # de Windows, a diferencia de Get-Counter).
        script = (
            "$p = Get-Process -Name 'ollama*','llama-server*' -ErrorAction SilentlyContinue; "
            "$ram = [long](($p | Measure-Object WorkingSet64 -Sum).Sum); "
            "$cpu = [long](($p | ForEach-Object { $_.TotalProcessorTime.TotalMilliseconds } | Measure-Object -Sum).Sum); "
            "Write-Output \"$ram;$cpu\""
        )
        nucleos = os.cpu_count() or 1
        anterior = None
        while self.activo:
            try:
                salida = subprocess.run(
                    ['powershell', '-NoProfile', '-Command', script],
                    capture_output=True, text=True, timeout=10,
                ).stdout.strip()
                ram_bytes, cpu_ms = (int(x) for x in salida.split(';'))
                ahora = time.perf_counter()
                if anterior:
                    transcurrido_ms = (ahora - anterior[0]) * 1000
                    cpu = max(0, (cpu_ms - anterior[1]) / transcurrido_ms / nucleos * 100)
                    self.muestras.append((round(ram_bytes / 1024 / 1024), round(cpu)))
                anterior = (ahora, cpu_ms)
            except Exception:
                pass
            time.sleep(1)


def consultar(base, token, pregunta):
    inicio = time.perf_counter()
    primer = None
    texto = ''
    fin = {}
    try:
        with post_json(f'{base}/api/asistente/chat/stream/', {'mensaje': pregunta}, token) as r:
            for linea in r:
                if not linea.strip():
                    continue
                evento = json.loads(linea)
                if evento.get('texto'):
                    if primer is None:
                        primer = time.perf_counter() - inicio
                    texto += evento['texto']
                if evento.get('error'):
                    return {'ok': False, 'texto': evento['error'], 'total': time.perf_counter() - inicio}
                if evento.get('fin'):
                    fin = evento
    except urllib.error.HTTPError as e:
        return {'ok': False, 'texto': f'HTTP {e.code}: {e.read().decode()[:200]}', 'total': time.perf_counter() - inicio}
    except Exception as e:  # noqa: BLE001 - se reporta cualquier falla
        return {'ok': False, 'texto': f'{type(e).__name__}: {e}', 'total': time.perf_counter() - inicio}

    return {
        'ok': True,
        'texto': texto.strip(),
        'total': time.perf_counter() - inicio,
        'primer': primer,
        'metricas': fin.get('metricas', {}),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--base', default='http://127.0.0.1:8000')
    parser.add_argument('--usuario', default='solicitante@emi.edu.bo')
    parser.add_argument('--clave', default='Hola123*')
    parser.add_argument('--n', type=int, default=len(BANCO_PREGUNTAS), help='cantidad de preguntas')
    parser.add_argument('--salida', default=None, help='archivo Markdown del reporte')
    args = parser.parse_args()

    with post_json(f'{args.base}/api/usuarios/login/', {'email': args.usuario, 'password': args.clave}) as r:
        token = json.load(r)['token']

    print('Calentando el modelo (la primera carga no se cuenta en el promedio)...')
    calentamiento = consultar(args.base, token, 'Hola')
    print(f'  carga inicial: {calentamiento["total"]:.1f} s')

    monitor = MonitorOllama()
    monitor.start()

    resultados = []
    preguntas = BANCO_PREGUNTAS[:args.n]
    for i, (categoria, pregunta) in enumerate(preguntas, 1):
        res = consultar(args.base, token, pregunta)
        res.update(n=i, categoria=categoria, pregunta=pregunta)
        resultados.append(res)
        primer = f'{res["primer"]:.1f}' if res.get('primer') else '-'
        print(f'[{i:02d}/{len(preguntas)}] {res["total"]:5.1f} s (1er fragmento {primer} s) {pregunta}')

    monitor.activo = False
    monitor.join(timeout=15)

    exitosas = [r for r in resultados if r['ok']]
    totales = [r['total'] for r in exitosas]
    primeros = [r['primer'] for r in exitosas if r.get('primer')]
    tps = [r['metricas'].get('tokens_por_segundo') for r in exitosas if r['metricas'].get('tokens_por_segundo')]
    ram = [m[0] for m in monitor.muestras]
    cpu = [m[1] for m in monitor.muestras]

    def fmt(valores, d=1):
        return f'{statistics.mean(valores):.{d}f}' if valores else '-'

    ahora = datetime.now()
    salida = Path(args.salida) if args.salida else (
        Path(__file__).resolve().parents[2] / 'docs' / 'asistente-ia' / '03-evidencias' / 'reportes'
        / f'rendimiento-{ahora:%Y%m%d-%H%M}-{args.usuario.split("@")[0]}.md'
    )
    salida.parent.mkdir(parents=True, exist_ok=True)

    lineas = [
        '# Reporte de rendimiento del asistente SIGTA-AI',
        '',
        f'- **Fecha:** {ahora:%d/%m/%Y %H:%M}',
        f'- **Usuario de prueba:** {args.usuario}',
        f'- **Consultas:** {len(resultados)} ({len(exitosas)} exitosas, {len(resultados) - len(exitosas)} fallidas)',
        f'- **Carga inicial del modelo (no incluida en el promedio):** {calentamiento["total"]:.1f} s',
        '- **Recorrido medido:** navegador simulado -> Django `/api/asistente/chat/stream/` -> Ollama -> respuesta completa',
        '',
        '## Resumen',
        '',
        '| Métrica | Valor |',
        '|---|---|',
        f'| Tiempo promedio hasta el primer fragmento | {fmt(primeros)} s |',
        f'| Tiempo promedio de respuesta completa | {fmt(totales)} s |',
        f'| Tiempo mínimo / máximo | {min(totales, default=0):.1f} s / {max(totales, default=0):.1f} s |',
        f'| Mediana de respuesta completa | {statistics.median(totales) if totales else 0:.1f} s |',
        f'| Velocidad de generación promedio | {fmt(tps)} tokens/s |',
        f'| RAM de Ollama (promedio / máximo) | {fmt(ram, 0)} MB / {max(ram, default=0)} MB |',
        f'| CPU de Ollama (promedio / máximo) | {fmt(cpu, 0)} % / {max(cpu, default=0)} % |',
        '',
        '## Detalle por consulta',
        '',
        '| # | Categoría | Pregunta | 1er fragmento (s) | Total (s) | Tokens | OK |',
        '|---|---|---|---|---|---|---|',
    ]
    for r in resultados:
        primer = f'{r["primer"]:.1f}' if r.get('primer') else '-'
        tokens = (r.get('metricas') or {}).get('tokens_respuesta') or '-'
        lineas.append(
            f'| {r["n"]} | {r["categoria"]} | {r["pregunta"]} | {primer} | {r["total"]:.1f} | {tokens} | {"✅" if r["ok"] else "❌"} |'
        )
    lineas += ['', '## Respuestas obtenidas', '']
    for r in resultados:
        lineas += [f'**{r["n"]}. {r["pregunta"]}**', '', '> ' + r['texto'].replace('\n', '\n> '), '']

    salida.write_text('\n'.join(lineas), encoding='utf-8')
    print(f'\nPromedio 1er fragmento: {fmt(primeros)} s | promedio total: {fmt(totales)} s | RAM máx: {max(ram, default=0)} MB')
    print(f'Reporte: {salida}')


if __name__ == '__main__':
    main()
