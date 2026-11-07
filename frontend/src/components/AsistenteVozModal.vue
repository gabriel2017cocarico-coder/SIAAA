<template>
  <div v-if="visible" class="asistente-ia">
    <!-- BOTÓN FLOTANTE -->
    <button
      v-if="!abierto"
      type="button"
      class="asistente-fab"
      aria-label="Abrir asistente virtual SIGTA-AI"
      title="Asistente virtual SIGTA-AI"
      @click="abrir"
    >
      <svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">
        <path fill="currentColor" d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73A2 2 0 0 1 12 2M7.5 13A2.5 2.5 0 0 0 5 15.5 2.5 2.5 0 0 0 7.5 18a2.5 2.5 0 0 0 2.5-2.5A2.5 2.5 0 0 0 7.5 13m9 0a2.5 2.5 0 0 0-2.5 2.5 2.5 2.5 0 0 0 2.5 2.5 2.5 2.5 0 0 0 2.5-2.5 2.5 2.5 0 0 0-2.5-2.5Z"/>
      </svg>
    </button>

    <!-- VENTANA DEL CHAT -->
    <section
      v-else
      class="asistente-panel"
      role="dialog"
      aria-label="Asistente virtual SIGTA-AI"
      @keydown.esc="cerrar"
    >
      <header class="asistente-cabecera">
        <div class="asistente-titulo">
          <strong>SIGTA-AI</strong>
          <span class="asistente-estado" :class="estadoClase">
            <span class="punto" aria-hidden="true"></span>{{ estadoTexto }}
          </span>
        </div>
        <div class="asistente-acciones">
          <button
            type="button"
            class="icono"
            :aria-label="silenciado ? 'Activar lectura en voz alta' : 'Silenciar lectura en voz alta'"
            :title="silenciado ? 'Activar voz' : 'Silenciar voz'"
            :disabled="!soportaVoz"
            @click="alternarSilencio"
          >{{ silenciado ? '🔇' : '🔊' }}</button>
          <button
            type="button"
            class="icono"
            aria-label="Repetir la última respuesta en voz alta"
            title="Repetir última respuesta"
            :disabled="!soportaVoz || !ultimaRespuesta"
            @click="repetir"
          >🔁</button>
          <button type="button" class="icono" aria-label="Cerrar asistente" title="Cerrar" @click="cerrar">✕</button>
        </div>
      </header>

      <div ref="listaRef" class="asistente-mensajes" aria-live="polite">
        <div v-if="!mensajes.length" class="asistente-bienvenida">
          <p>Hola, soy <strong>SIGTA-AI</strong>. Puedo informarte sobre tus tickets, requerimientos de mantenimiento y compras, y orientarte en el uso del sistema.</p>
          <p class="sugerencias-titulo">Prueba con:</p>
          <button
            v-for="s in sugerencias"
            :key="s"
            type="button"
            class="sugerencia"
            :disabled="enviando"
            @click="enviar(s)"
          >{{ s }}</button>
        </div>

        <div
          v-for="(m, i) in mensajes"
          :key="i"
          class="burbuja"
          :class="[m.rol, { error: m.error }]"
        >
          <span v-if="m.texto">{{ m.texto }}</span>
          <span v-else class="escribiendo" aria-label="El asistente está escribiendo">
            <i></i><i></i><i></i>
          </span>
          <small v-if="m.duracionMs" class="meta">{{ (m.duracionMs / 1000).toFixed(1) }} s</small>
        </div>
      </div>

      <p v-if="avisoVoz" class="asistente-aviso" role="status">{{ avisoVoz }}</p>

      <form class="asistente-entrada" @submit.prevent="enviar()">
        <button
          v-if="soportaMicrofono"
          type="button"
          class="microfono"
          :class="{ escuchando }"
          :aria-label="escuchando ? 'Detener micrófono' : 'Hablar por micrófono'"
          :title="escuchando ? 'Escuchando… pulsa para detener' : 'Hablar'"
          :disabled="enviando"
          @click="alternarMicrofono"
        >🎤</button>
        <input
          ref="entradaRef"
          v-model="texto"
          type="text"
          :placeholder="escuchando ? 'Escuchando…' : 'Escribe tu pregunta…'"
          :maxlength="1000"
          :disabled="enviando"
          aria-label="Pregunta para el asistente"
        />
        <button type="submit" class="enviar" :disabled="enviando || !texto.trim()" aria-label="Enviar pregunta">➤</button>
      </form>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const sugerencias = [
  '¿Qué tickets tengo pendientes?',
  '¿Cómo registro un ticket de soporte?',
  '¿Cuál es el límite de Caja Chica?',
]

/* ---------------------------------------------------------
   ESTADO
--------------------------------------------------------- */
const abierto = ref(false)
const texto = ref('')
const mensajes = ref([])
const enviando = ref(false)
const escuchando = ref(false)
const silenciado = ref(localStorage.getItem('sigta_asistente_silenciado') === '1')
const avisoVoz = ref('')
const estadoServicio = ref('desconocido') // desconocido | listo | sin-modelo | caido
const listaRef = ref(null)
const entradaRef = ref(null)

let reconocimiento = null
let controlador = null

const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition
const soportaMicrofono = !!SpeechRecognitionAPI
const soportaVoz = 'speechSynthesis' in window

// Solo con sesión iniciada y fuera del cambio obligatorio de contraseña.
const visible = computed(() =>
  !!route.meta?.requiereAuth &&
  route.name !== 'cambiar-contrasena' &&
  !!localStorage.getItem('sigta_token')
)

const ultimaRespuesta = computed(() => {
  for (let i = mensajes.value.length - 1; i >= 0; i--) {
    const m = mensajes.value[i]
    if (m.rol === 'asistente' && m.texto && !m.error) return m.texto
  }
  return ''
})

const estadoTexto = computed(() => ({
  listo: 'En línea',
  'sin-modelo': 'Modelo no instalado',
  caido: 'Sin conexión',
  desconocido: 'Verificando…',
}[estadoServicio.value]))

const estadoClase = computed(() => `estado-${estadoServicio.value}`)

// Al cerrar sesión se descarta la conversación.
watch(visible, (v) => {
  if (!v) {
    detenerTodo()
    abierto.value = false
    mensajes.value = []
  }
})

/* ---------------------------------------------------------
   UTILIDADES
--------------------------------------------------------- */
function cabeceras() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Token ${localStorage.getItem('sigta_token')}`,
  }
}

async function desplazarAbajo() {
  await nextTick()
  if (listaRef.value) listaRef.value.scrollTop = listaRef.value.scrollHeight
}

function sesionExpirada() {
  localStorage.removeItem('sigta_token')
  localStorage.removeItem('sigta_usuario')
  router.push('/login')
}

async function verificarEstado() {
  try {
    const r = await fetch('/api/asistente/estado/', { headers: cabeceras() })
    if (r.status === 401) return sesionExpirada()
    const d = await r.json()
    estadoServicio.value = !d.ollama ? 'caido' : d.modelo_instalado ? 'listo' : 'sin-modelo'
  } catch {
    estadoServicio.value = 'caido'
  }
}

/* ---------------------------------------------------------
   APERTURA / CIERRE
--------------------------------------------------------- */
async function abrir() {
  abierto.value = true
  verificarEstado()
  await nextTick()
  entradaRef.value?.focus()
  desplazarAbajo()
}

function cerrar() {
  detenerTodo()
  abierto.value = false
}

function detenerTodo() {
  controlador?.abort()
  detenerMicrofono()
  if (soportaVoz) window.speechSynthesis.cancel()
}

/* ---------------------------------------------------------
   ENVÍO DE MENSAJES (respuesta en streaming)
--------------------------------------------------------- */
async function enviar(textoForzado) {
  const pregunta = (textoForzado ?? texto.value).trim()
  if (!pregunta || enviando.value) return

  detenerMicrofono()
  if (soportaVoz) window.speechSynthesis.cancel()
  avisoVoz.value = ''

  const historial = mensajes.value
    .filter((m) => m.texto && !m.error)
    .slice(-4)
    .map((m) => ({ rol: m.rol, texto: m.texto }))

  mensajes.value.push({ rol: 'usuario', texto: pregunta })
  mensajes.value.push({ rol: 'asistente', texto: '', error: false, duracionMs: null })
  // Se usa el proxy reactivo del arreglo para que la vista se actualice.
  const actual = mensajes.value[mensajes.value.length - 1]
  texto.value = ''
  enviando.value = true
  desplazarAbajo()

  controlador = new AbortController()
  try {
    const r = await fetch('/api/asistente/chat/stream/', {
      method: 'POST',
      headers: cabeceras(),
      body: JSON.stringify({ mensaje: pregunta, historial }),
      signal: controlador.signal,
    })

    if (r.status === 401) {
      sesionExpirada()
      return
    }
    if (!r.ok) {
      let detalle = 'El asistente no está disponible en este momento.'
      try { detalle = (await r.json()).error || detalle } catch { /* respuesta sin JSON */ }
      if (r.status === 503) estadoServicio.value = 'caido'
      throw new Error(detalle)
    }

    estadoServicio.value = 'listo'
    await leerStream(r, actual)
    if (!actual.texto) actual.texto = 'No pude generar una respuesta. Intenta reformular la pregunta.'
    if (!actual.error) hablar(actual.texto)
  } catch (e) {
    if (e.name === 'AbortError') {
      if (!actual.texto) mensajes.value.splice(mensajes.value.indexOf(actual), 1)
    } else {
      actual.error = true
      actual.texto = e.message === 'Failed to fetch'
        ? 'No hay conexión con el servidor de SIGTA.'
        : e.message
    }
  } finally {
    enviando.value = false
    controlador = null
    desplazarAbajo()
    await nextTick()
    entradaRef.value?.focus()
  }
}

async function leerStream(respuestaHttp, actual) {
  const lector = respuestaHttp.body.getReader()
  const decodificador = new TextDecoder()
  let pendiente = ''

  const procesar = (linea) => {
    if (!linea.trim()) return
    let evento
    try { evento = JSON.parse(linea) } catch { return }
    if (evento.texto) {
      actual.texto += evento.texto
      desplazarAbajo()
    }
    if (evento.error) throw new Error(evento.error)
    if (evento.fin) actual.duracionMs = evento.duracion_ms
  }

  for (;;) {
    const { done, value } = await lector.read()
    if (done) break
    pendiente += decodificador.decode(value, { stream: true })
    const lineas = pendiente.split('\n')
    pendiente = lineas.pop()
    lineas.forEach(procesar)
  }
  procesar(pendiente)
  actual.texto = actual.texto.trim()
}

/* ---------------------------------------------------------
   VOZ A TEXTO (SpeechRecognition)
--------------------------------------------------------- */
function alternarMicrofono() {
  if (escuchando.value) {
    detenerMicrofono()
  } else {
    iniciarMicrofono()
  }
}

function iniciarMicrofono() {
  if (!soportaMicrofono) return
  if (soportaVoz) window.speechSynthesis.cancel()
  avisoVoz.value = ''

  reconocimiento = new SpeechRecognitionAPI()
  reconocimiento.lang = 'es-ES'
  reconocimiento.interimResults = true
  reconocimiento.continuous = false
  reconocimiento.maxAlternatives = 1

  let final = ''

  reconocimiento.onresult = (evento) => {
    let parcial = ''
    for (let i = evento.resultIndex; i < evento.results.length; i++) {
      const fragmento = evento.results[i][0].transcript
      if (evento.results[i].isFinal) final += fragmento
      else parcial += fragmento
    }
    texto.value = (final + parcial).trim()
  }

  reconocimiento.onerror = (evento) => {
    const mensajesError = {
      'not-allowed': 'Permiso de micrófono denegado. Haz clic en el candado de la barra de direcciones y permite el micrófono.',
      'service-not-allowed': 'El navegador no permite usar el micrófono en esta página.',
      'no-speech': 'No te escuché. Pulsa el micrófono e intenta de nuevo.',
      'audio-capture': 'No se encontró un micrófono conectado.',
      network: 'El reconocimiento de voz necesita conexión a internet.',
    }
    if (evento.error !== 'aborted') {
      avisoVoz.value = mensajesError[evento.error] || 'No se pudo usar el micrófono. Escribe tu pregunta.'
    }
  }

  reconocimiento.onend = () => {
    escuchando.value = false
    reconocimiento = null
    // Se envía automáticamente lo dictado.
    if (final.trim() && !enviando.value) enviar(final)
  }

  try {
    reconocimiento.start()
    escuchando.value = true
  } catch {
    escuchando.value = false
    avisoVoz.value = 'No se pudo iniciar el micrófono.'
  }
}

function detenerMicrofono() {
  if (reconocimiento) {
    try { reconocimiento.stop() } catch { /* ya detenido */ }
  }
  escuchando.value = false
}

/* ---------------------------------------------------------
   TEXTO A VOZ (speechSynthesis)
--------------------------------------------------------- */
function vozEspanol() {
  const voces = window.speechSynthesis.getVoices()
  return (
    voces.find((v) => v.lang === 'es-BO') ||
    voces.find((v) => v.lang?.startsWith('es') && /Google|Microsoft/.test(v.name)) ||
    voces.find((v) => v.lang?.startsWith('es')) ||
    null
  )
}

function hablar(contenido, forzar = false) {
  if (!soportaVoz || (silenciado.value && !forzar) || !contenido) return
  window.speechSynthesis.cancel()

  const limpio = contenido.replace(/[*#_`>|]/g, ' ').replace(/\s+/g, ' ').trim()
  // Chrome corta las locuciones largas: se lee por oraciones.
  const oraciones = limpio.match(/[^.!?]+[.!?]*/g) || [limpio]
  const voz = vozEspanol()

  oraciones.forEach((oracion) => {
    const locucion = new SpeechSynthesisUtterance(oracion.trim())
    locucion.lang = voz?.lang || 'es-ES'
    if (voz) locucion.voice = voz
    locucion.rate = 1
    window.speechSynthesis.speak(locucion)
  })
}

function alternarSilencio() {
  silenciado.value = !silenciado.value
  localStorage.setItem('sigta_asistente_silenciado', silenciado.value ? '1' : '0')
  if (silenciado.value) window.speechSynthesis.cancel()
}

function repetir() {
  hablar(ultimaRespuesta.value, true)
}

// Algunas versiones de Chrome cargan las voces de forma diferida.
if (soportaVoz) window.speechSynthesis.getVoices()

onBeforeUnmount(detenerTodo)
</script>

<style scoped>
.asistente-ia {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 2000;
  font-family: inherit;
}

.asistente-fab {
  width: 60px;
  height: 60px;
  border: 3px solid var(--sigta-mostaza, #FFC72C);
  border-radius: 50%;
  background: var(--sigta-azul, #123A6B);
  color: #fff;
  display: grid;
  place-items: center;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(12, 42, 79, 0.35);
  transition: transform 0.15s ease, background 0.15s ease;
}

.asistente-fab:hover,
.asistente-fab:focus-visible {
  transform: scale(1.07);
  background: var(--sigta-azul-medio, #1D5090);
}

.asistente-panel {
  width: min(380px, calc(100vw - 32px));
  height: min(560px, calc(100vh - 48px));
  display: flex;
  flex-direction: column;
  background: var(--sigta-superficie, #fff);
  border: 1px solid var(--sigta-borde, #D7E3EF);
  border-radius: 16px;
  box-shadow: 0 12px 36px rgba(12, 42, 79, 0.28);
  overflow: hidden;
}

.asistente-cabecera {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: var(--sigta-azul, #123A6B);
  color: #fff;
  border-bottom: 3px solid var(--sigta-mostaza, #FFC72C);
}

.asistente-titulo {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.asistente-estado {
  font-size: 12px;
  opacity: 0.9;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.asistente-estado .punto {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #9fb3c8;
}

.estado-listo .punto { background: #3ddc84; }
.estado-caido .punto,
.estado-sin-modelo .punto { background: #ff6b5e; }

.asistente-acciones {
  display: flex;
  gap: 4px;
}

.icono {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 16px;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
}

.icono:hover:not(:disabled) { background: rgba(255, 255, 255, 0.15); }
.icono:disabled { opacity: 0.4; cursor: default; }

.asistente-mensajes {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
  background: var(--sigta-fondo, #F4F8FC);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.asistente-bienvenida {
  color: var(--sigta-texto, #14304F);
  font-size: 14px;
}

.asistente-bienvenida p { margin: 0 0 10px; }

.sugerencias-titulo {
  font-weight: 600;
  color: var(--sigta-texto-suave, #5B7189);
}

.sugerencia {
  display: block;
  width: 100%;
  text-align: left;
  margin-bottom: 6px;
  padding: 8px 10px;
  border: 1px solid var(--sigta-azul-texto-claro, #C2DBF2);
  border-radius: 10px;
  background: #fff;
  color: var(--sigta-azul, #123A6B);
  cursor: pointer;
  font-size: 13px;
}

.sugerencia:hover:not(:disabled) { background: var(--sigta-azul-claro, #DDE9F5); }

.burbuja {
  max-width: 85%;
  padding: 9px 12px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.45;
  white-space: pre-wrap;
  word-wrap: break-word;
  display: flex;
  flex-direction: column;
}

.burbuja.usuario {
  align-self: flex-end;
  background: var(--sigta-azul, #123A6B);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.burbuja.asistente {
  align-self: flex-start;
  background: #fff;
  color: var(--sigta-texto, #14304F);
  border: 1px solid var(--sigta-borde, #D7E3EF);
  border-bottom-left-radius: 4px;
}

.burbuja.error {
  background: var(--sigta-error-fondo, #FDECEB);
  color: var(--sigta-error, #B42318);
  border-color: transparent;
}

.meta {
  align-self: flex-end;
  font-size: 11px;
  opacity: 0.6;
  margin-top: 3px;
}

.escribiendo {
  display: inline-flex;
  gap: 4px;
  padding: 4px 0;
}

.escribiendo i {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--sigta-texto-tenue, #8CA0B4);
  animation: rebote 1.2s infinite ease-in-out;
}

.escribiendo i:nth-child(2) { animation-delay: 0.15s; }
.escribiendo i:nth-child(3) { animation-delay: 0.3s; }

@keyframes rebote {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.5; }
  40% { transform: translateY(-5px); opacity: 1; }
}

.asistente-aviso {
  margin: 0;
  padding: 8px 14px;
  font-size: 12px;
  background: var(--sigta-mostaza-suave, #FFF8DA);
  color: var(--sigta-texto, #14304F);
  border-top: 1px solid var(--sigta-borde, #D7E3EF);
}

.asistente-entrada {
  display: flex;
  gap: 8px;
  padding: 10px;
  border-top: 1px solid var(--sigta-borde, #D7E3EF);
  background: #fff;
}

.asistente-entrada input {
  flex: 1;
  min-width: 0;
  padding: 9px 12px;
  border: 1px solid var(--sigta-borde, #D7E3EF);
  border-radius: 20px;
  font-size: 14px;
  color: var(--sigta-texto, #14304F);
  outline: none;
}

.asistente-entrada input:focus { border-color: var(--sigta-azul-medio, #1D5090); }

.microfono,
.enviar {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  font-size: 17px;
  display: grid;
  place-items: center;
}

.microfono {
  background: var(--sigta-azul-claro, #DDE9F5);
}

.microfono.escuchando {
  background: var(--sigta-error, #B42318);
  animation: pulso 1.2s infinite;
}

@keyframes pulso {
  0% { box-shadow: 0 0 0 0 rgba(180, 35, 24, 0.55); }
  70% { box-shadow: 0 0 0 12px rgba(180, 35, 24, 0); }
  100% { box-shadow: 0 0 0 0 rgba(180, 35, 24, 0); }
}

.enviar {
  background: var(--sigta-mostaza, #FFC72C);
  color: var(--sigta-azul-oscuro, #0C2A4F);
}

.microfono:disabled,
.enviar:disabled { opacity: 0.45; cursor: default; }

@media (max-width: 480px) {
  .asistente-ia { right: 12px; bottom: 12px; }
}
</style>
