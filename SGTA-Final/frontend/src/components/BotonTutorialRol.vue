<template>
  <div v-if="autenticado" class="sia-tutorial-contenedor">
    <!-- ===================================================
         BOTÓN FLOTANTE (FAB) — AYUDA / ASISTENCIA DEL ROL
         Mismo estilo institucional que Tati (azul marino y dorado)
         =================================================== -->
    <button
      ref="fabRef"
      class="sia-tutorial-fab"
      :class="{ 'sia-tutorial-fab--activo': modalAbierto }"
      @click="toggleModal"
      title="Ayuda y guía de uso"
      aria-label="Abrir ayuda en video del rol"
    >
      <!-- Icono de Ayuda / Asistencia (?) -->
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="26" height="26">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-4h2v2h-2v-2zm1.61-9.96c-2.06-.3-3.88.97-4.43 2.79-.18.58.26 1.17.87 1.17h.2c.41 0 .74-.29.88-.67.32-.89 1.27-1.5 2.3-1.28.95.2 1.65 1.13 1.57 2.1-.1 1.34-1.62 1.63-2.45 2.88 0 .01-.01.01-.01.02-.01.02-.02.03-.03.05-.09.15-.18.32-.25.5-.01.03-.03.05-.04.08-.01.02-.01.04-.02.07-.12.34-.2.75-.2 1.25h2c0-.42.11-.77.28-1.07.02-.03.03-.06.05-.09.08-.14.18-.27.28-.39.01-.01.02-.03.03-.04.1-.12.21-.23.33-.34.96-.91 2.26-1.65 1.99-3.56-.24-1.74-1.61-3.21-3.35-3.47z"/>
      </svg>
    </button>

    <!-- Tooltip discreto la primera vez -->
    <div v-if="mostrarTooltip && !modalAbierto" class="sia-tutorial-tooltip" role="tooltip">
      <span><strong>Ayuda:</strong> Ver guía en video de tu rol</span>
      <button class="sia-tutorial-tooltip__cerrar" @click.stop="cerrarTooltip" aria-label="Cerrar aviso">✕</button>
    </div>

    <!-- ===================================================
         MODAL MINIMALISTA — SOLO EL VIDEO EN GRANDE Y BOTÓN X
         =================================================== -->
    <Transition name="sia-modal-fade">
      <div v-if="modalAbierto" class="sia-tutorial-backdrop" @click.self="cerrarModal">
        <div class="sia-tutorial-modal" role="dialog" aria-modal="true" aria-label="Video guía del sistema">
          <button
            class="sia-tutorial-modal__btn-cerrar"
            @click="cerrarModal"
            title="Cerrar"
            aria-label="Cerrar video"
          >
            ✕
          </button>

          <video
            ref="videoRef"
            :src="videoUrlActual"
            controls
            autoplay
            playsinline
            class="sia-tutorial-video"
          >
            Tu navegador no soporta el formato de video MP4.
          </video>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const modalAbierto = ref(false)
const mostrarTooltip = ref(false)
const videoRef = ref(null)

/* ============================================================
   AUTENTICACIÓN Y ROL ACTIVO (Sincronizado con AsistenteChat)
   ============================================================ */
const rawToken = ref(localStorage.getItem('sigta_token') || '')
const rawUsuario = ref(localStorage.getItem('sigta_usuario') || '')

function actualizarSesion() {
  rawToken.value = localStorage.getItem('sigta_token') || ''
  rawUsuario.value = localStorage.getItem('sigta_usuario') || ''
}

watch(() => route.path, () => {
  actualizarSesion()
})

const autenticado = computed(() => {
  if (!route.path || route.path === '/login' || route.path === '/recuperar-contrasena') {
    return false
  }
  return !!(rawToken.value || localStorage.getItem('sigta_token'))
})

const rolActivo = computed(() => {
  const path = route.path || ''
  if (path.startsWith('/auxiliar-servicios-generales')) return 'AUXILIAR_SERVICIOS_GENERALES'
  if (path.startsWith('/servicios-generales')) return 'SERVICIOS_GENERALES'
  if (path.startsWith('/especialista')) return 'ESPECIALISTA'
  if (path.startsWith('/jefe-utic')) return 'JEFE_UTIC'
  if (path.startsWith('/tesoreria')) return 'TESORERIA'
  if (path.startsWith('/almacen')) return 'ENCARGADO_COMPRAS_ALMACEN'
  if (path.startsWith('/daf')) return 'DAF'
  if (path.startsWith('/superuser')) return 'SUPERUSER'
  if (path.startsWith('/admin')) return 'ADMIN'
  if (path.startsWith('/usuario')) return 'SOLICITANTE'

  try {
    const u = JSON.parse(rawUsuario.value || localStorage.getItem('sigta_usuario') || '{}')
    const roles = Array.isArray(u.roles) ? u.roles.map(r => (typeof r === 'string' ? r : r.codigo)) : []
    const orden = [
      'AUXILIAR_SERVICIOS_GENERALES',
      'ESPECIALISTA',
      'SERVICIOS_GENERALES',
      'JEFE_UTIC',
      'DAF',
      'JEFE_DAF',
      'TESORERIA',
      'ENCARGADO_COMPRAS_ALMACEN',
      'ADMIN',
      'SUPERUSER',
      'DIRECTOR',
      'JEFE_CARRERA',
      'SOLICITANTE'
    ]
    for (const r of orden) {
      if (roles.includes(r)) return r
    }
    if (roles.length > 0) return roles[0]
  } catch {}
  return 'SOLICITANTE'
})

const VIDEOS_POR_ROL = {
  SOLICITANTE: '/videos/tutoriales/tutorial_solicitante.mp4',
  JEFE_UTIC: '/videos/tutoriales/tutorial_jefe_utic.mp4',
  ESPECIALISTA: '/videos/tutoriales/tutorial_especialista.mp4',
  SERVICIOS_GENERALES: '/videos/tutoriales/tutorial_servicios_generales.mp4',
  AUXILIAR_SERVICIOS_GENERALES: '/videos/tutoriales/tutorial_auxiliar_servicios_generales.mp4',
  DAF: '/videos/tutoriales/tutorial_daf.mp4',
  JEFE_DAF: '/videos/tutoriales/tutorial_daf.mp4',
  TESORERIA: '/videos/tutoriales/tutorial_tesoreria.mp4',
  ENCARGADO_COMPRAS_ALMACEN: '/videos/tutoriales/tutorial_almacen.mp4',
  ADMIN: '/videos/tutoriales/tutorial_admin.mp4',
  SUPERUSER: '/videos/tutoriales/tutorial_superuser.mp4',
  DIRECTOR: '/videos/tutoriales/tutorial_admin.mp4',
  JEFE_CARRERA: '/videos/tutoriales/tutorial_solicitante.mp4'
}

const videoUrlActual = computed(() => {
  return VIDEOS_POR_ROL[rolActivo.value] || VIDEOS_POR_ROL.SOLICITANTE
})

function toggleModal() {
  if (modalAbierto.value) {
    cerrarModal()
  } else {
    modalAbierto.value = true
    mostrarTooltip.value = false
  }
}

function cerrarModal() {
  modalAbierto.value = false
  if (videoRef.value) {
    videoRef.value.pause()
  }
}

function cerrarTooltip() {
  mostrarTooltip.value = false
  localStorage.setItem('sia_tutorial_tooltip_visto', 'true')
}

function onKeyDown(e) {
  if (e.key === 'Escape' && modalAbierto.value) {
    cerrarModal()
  }
}

let sessionTimer = null

function evaluarTooltip() {
  const visto = localStorage.getItem('sia_tutorial_tooltip_visto')
  if (!visto && autenticado.value) {
    setTimeout(() => {
      if (!modalAbierto.value && autenticado.value) mostrarTooltip.value = true
    }, 2500)
  }
}

watch(autenticado, (nuevo) => {
  if (nuevo) evaluarTooltip()
})

onMounted(() => {
  actualizarSesion()
  window.addEventListener('storage', actualizarSesion)
  window.addEventListener('keydown', onKeyDown)
  sessionTimer = setInterval(actualizarSesion, 1000)
  evaluarTooltip()
})

onUnmounted(() => {
  window.removeEventListener('storage', actualizarSesion)
  window.removeEventListener('keydown', onKeyDown)
  if (sessionTimer) clearInterval(sessionTimer)
})
</script>

<style scoped>
.sia-tutorial-contenedor {
  position: relative;
  font-family: inherit;
}

/* ============================================================
   BOTÓN FLOTANTE (FAB) — MISMO ESTILO QUE TATI
   ============================================================ */
.sia-tutorial-fab {
  position: fixed !important;
  bottom: 28px !important;
  right: 96px !important;
  z-index: 999998 !important;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0C2A4F 0%, #123A6B 100%);
  color: #FFC72C;
  border: 2px solid rgba(255, 199, 44, 0.45);
  box-shadow: 0 8px 24px rgba(12, 42, 79, 0.35), 0 0 0 0 rgba(255, 199, 44, 0.3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.25s, border-color 0.25s;
}

.sia-tutorial-fab:hover {
  transform: translateY(-3px) scale(1.05);
  border-color: #FFC72C;
  box-shadow: 0 12px 28px rgba(12, 42, 79, 0.45);
}

.sia-tutorial-fab--activo {
  border-color: #FFC72C;
  box-shadow: 0 4px 18px rgba(12, 42, 79, 0.5);
  transform: scale(0.96);
}

.sia-tutorial-tooltip {
  position: fixed;
  bottom: 96px;
  right: 96px;
  z-index: 999997;
  background: #0C2A4F;
  color: #FFFFFF;
  border: 1px solid rgba(255, 199, 44, 0.5);
  padding: 9px 14px;
  border-radius: 12px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  animation: floatTooltip 3s ease-in-out infinite;
}

.sia-tutorial-tooltip strong {
  color: #FFC72C;
}

.sia-tutorial-tooltip__cerrar {
  background: transparent;
  border: none;
  color: #A0B6CD;
  cursor: pointer;
  font-size: 14px;
  padding: 0 2px;
}

.sia-tutorial-tooltip__cerrar:hover {
  color: #FFFFFF;
}

@keyframes floatTooltip {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

/* ============================================================
   MODAL MINIMALISTA — SOLO VIDEO EN GRANDE + BOTÓN X
   ============================================================ */
.sia-tutorial-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(8, 20, 38, 0.85);
  backdrop-filter: blur(6px);
  z-index: 9999999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.sia-tutorial-modal {
  position: relative;
  width: 100%;
  max-width: 1120px;
  background: #000000;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(255, 199, 44, 0.35);
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
}

.sia-tutorial-video {
  width: 100%;
  max-height: 85vh;
  display: block;
  background: #000000;
  outline: none;
}

.sia-tutorial-modal__btn-cerrar {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 10;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(12, 42, 79, 0.88);
  color: #FFFFFF;
  border: 1.5px solid rgba(255, 199, 44, 0.65);
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.2s, border-color 0.2s;
}

.sia-tutorial-modal__btn-cerrar:hover {
  background: #FFC72C;
  color: #0C2A4F;
  border-color: #FFC72C;
  transform: scale(1.08);
}

.sia-modal-fade-enter-active,
.sia-modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.sia-modal-fade-enter-from,
.sia-modal-fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .sia-tutorial-backdrop {
    padding: 12px;
  }
  .sia-tutorial-fab {
    right: 88px !important;
    bottom: 20px !important;
  }
}
</style>
