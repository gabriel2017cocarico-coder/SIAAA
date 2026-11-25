<template>
  <div v-if="autenticado" class="sia-tutorial-contenedor">
    <!-- ===================================================
         BOTÓN FLOTANTE (FAB) — TUTORIALES Y GUÍAS DEL ROL
         Idéntico en estilo, sombra y elevación a AsistenteChat
         =================================================== -->
    <button
      ref="fabRef"
      class="sia-tutorial-fab"
      :class="{ 'sia-tutorial-fab--activo': modalAbierto }"
      @click="toggleModal"
      :title="`Video Tutorial Oficial: ${datosRolActual.titulo} (Clic para ver)`"
      aria-label="Abrir video tutorial del rol"
    >
      <!-- Icono de Cámara / Video Claqueta con birrete -->
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="26" height="26">
        <path d="M4 4h10a2 2 0 0 1 2 2v1.59l4.29-2.86A1 1 0 0 1 22 5.57v12.86a1 1 0 0 1-1.71.84L16 16.41V18a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm0 2v12h10V6H4zm12 3.59v4.82l4 2.67V6.92l-4 2.67zM9.5 8.5l4 3.5-4 3.5v-7z"/>
      </svg>

      <!-- Badge de ayuda -->
      <span class="sia-tutorial-fab__badge" aria-hidden="true">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="8" height="8">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 16h-2v-2h2v2zm1.07-7.75l-.9.92C12.45 11.9 12 12.5 12 14h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H7c0-2.76 2.24-5 5-5s5 2.24 5 5c0 .88-.36 1.68-.93 2.25z"/>
        </svg>
      </span>
    </button>

    <!-- Tooltip Flotante de Bienvenida/Ayuda -->
    <div v-if="mostrarTooltip && !modalAbierto" class="sia-tutorial-tooltip" role="tooltip">
      <span>🎥 <strong>Tutorial del Rol:</strong> Aprende tus funciones y atajos</span>
      <button class="sia-tutorial-tooltip__cerrar" @click.stop="cerrarTooltip">✕</button>
    </div>

    <!-- ===================================================
         MODAL DE VIDEO TUTORIAL — PANTALLA COMPLETA / CINE
         =================================================== -->
    <Transition name="sia-modal-fade">
      <div v-if="modalAbierto" class="sia-tutorial-backdrop" @click.self="cerrarModal">
        <div class="sia-tutorial-modal" role="dialog" aria-modal="true">
          <!-- Cabecera del Modal -->
          <div class="sia-tutorial-modal__header">
            <div class="sia-tutorial-modal__titulo-bloque">
              <span class="sia-tutorial-modal__insignia">GUÍA OFICIAL SIA</span>
              <h2 class="sia-tutorial-modal__titulo">{{ datosRolActual.titulo }}</h2>
              <p class="sia-tutorial-modal__subtitulo">{{ datosRolActual.descripcion }}</p>
            </div>
            <button class="sia-tutorial-modal__btn-cerrar" @click="cerrarModal" title="Cerrar video tutorial">
              ✕
            </button>
          </div>

          <!-- Cuerpo: Reproductor + Capítulos -->
          <div class="sia-tutorial-modal__cuerpo">
            <!-- Columna Reproductor -->
            <div class="sia-tutorial-modal__reproductor-col">
              <div class="sia-tutorial-video-wrapper">
                <video
                  ref="videoRef"
                  :src="datosRolActual.video"
                  controls
                  autoplay
                  playsinline
                  class="sia-tutorial-video"
                  @play="onVideoPlay"
                  @pause="onVideoPause"
                >
                  Tu navegador no soporta el formato de video MP4.
                </video>
              </div>

              <!-- Barra de Estado / Atajos -->
              <div class="sia-tutorial-info-card">
                <div class="sia-tutorial-info-card__item">
                  <span class="sia-tutorial-info-card__label">Asistente IA:</span>
                  <span class="sia-tutorial-info-card__valor">Tati disponible por Voz y Texto</span>
                </div>
                <div class="sia-tutorial-info-card__item">
                  <span class="sia-tutorial-info-card__label">Duración:</span>
                  <span class="sia-tutorial-info-card__valor">{{ datosRolActual.duracion || '4:15 min' }}</span>
                </div>
                <div class="sia-tutorial-info-card__item">
                  <span class="sia-tutorial-info-card__label">Calidad:</span>
                  <span class="sia-tutorial-info-card__valor">1080p HD con Voz Neuronal</span>
                </div>
              </div>
            </div>

            <!-- Columna Capítulos / Contenido -->
            <div class="sia-tutorial-modal__capitulos-col">
              <h3 class="sia-tutorial-capitulos__titulo">Contenido del Tutorial</h3>
              <ul class="sia-tutorial-capitulos__lista">
                <li
                  v-for="(cap, idx) in datosRolActual.capitulos"
                  :key="idx"
                  class="sia-tutorial-capitulo-item"
                  @click="saltarATiempo(cap.segundos)"
                >
                  <span class="sia-tutorial-capitulo__tiempo">{{ cap.tiempo }}</span>
                  <div class="sia-tutorial-capitulo__textos">
                    <strong>{{ cap.titulo }}</strong>
                    <small>{{ cap.detalle }}</small>
                  </div>
                </li>
              </ul>

              <!-- Tarjeta de soporte rápido -->
              <div class="sia-tutorial-asistente-banner">
                <div class="sia-tutorial-asistente-banner__icono">🤖</div>
                <div class="sia-tutorial-asistente-banner__texto">
                  <strong>¿Tienes dudas sobre tu rol?</strong>
                  <p>Abre a Tati en la esquina inferior para preguntarle por voz o texto en cualquier momento.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Pie del Modal -->
          <div class="sia-tutorial-modal__footer">
            <span class="sia-tutorial-modal__nota">
              Escuela Militar de Ingeniería — Sistema Integrado Administrativo (SIA)
            </span>
            <button class="sia-tutorial-btn-entendido" @click="cerrarModal">
              Entendido, volver al sistema
            </button>
          </div>
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
  if (path.startsWith('/admin') || path.startsWith('/superuser')) return 'ADMIN'
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

/* ============================================================
   CATÁLOGO DE VIDEOS Y CAPÍTULOS POR ROL
   ============================================================ */
const CATALOGO_ROLES = {
  SOLICITANTE: {
    titulo: 'Rol Solicitante / Usuario General',
    descripcion: 'Aprende a navegar el menú lateral, crear solicitudes con evidencia y consultar a Tati.',
    duracion: '4:20 min',
    video: '/videos/tutoriales/tutorial_solicitante.mp4',
    capitulos: [
      { tiempo: '00:00', segundos: 0, titulo: 'Bienvenida y Menú Lateral', detalle: 'Exploración de las 6 secciones del portal' },
      { tiempo: '01:45', segundos: 105, titulo: 'Registro de Solicitudes con Evidencia', detalle: 'Llenado de formulario, fotos y código de ticket' },
      { tiempo: '03:00', segundos: 180, titulo: 'Uso del Asistente IA (Tati)', detalle: 'Consulta de urgencia y navegación por voz' },
      { tiempo: '04:00', segundos: 240, titulo: 'Verificaciones y Cierre Seguro', detalle: 'Aprobación de trabajos y cierre de sesión' }
    ]
  },
  JEFE_UTIC: {
    titulo: 'Rol Jefe UTIC (Sistemas y Redes)',
    descripcion: 'Gestión de incidentes TI, clasificación de SLA, asignación equitativa y viabilidad técnica.',
    duracion: '3:50 min',
    video: '/videos/tutoriales/tutorial_jefe_utic.mp4',
    capitulos: [
      { tiempo: '00:00', segundos: 0, titulo: 'Consola UTIC y Menú', detalle: 'Bandeja de gestión y validación de usuarios' },
      { tiempo: '01:30', segundos: 90, titulo: 'Clasificación SLA y Asignación', detalle: 'Priorización y tope de 5 tickets por técnico' },
      { tiempo: '02:50', segundos: 170, titulo: 'Consultas con la IA (Tati)', detalle: 'Resumen de tickets pendientes y SLA normativo' },
      { tiempo: '03:30', segundos: 210, titulo: 'Viabilidad Técnica de Compras', detalle: 'Dictamen técnico para adquisición de equipos' }
    ]
  },
  ESPECIALISTA: {
    titulo: 'Rol Especialista de Soporte Técnico',
    descripcion: 'Atención de órdenes técnicas, diagnóstico en campo, solicitud de repuestos y cierre de trabajos.',
    duracion: '3:50 min',
    video: '/videos/tutoriales/tutorial_especialista.mp4',
    capitulos: [
      { tiempo: '00:00', segundos: 0, titulo: 'Bandeja de Trabajo y Menú', detalle: 'Órdenes nuevas vs trabajos en proceso con SLA' },
      { tiempo: '01:30', segundos: 90, titulo: 'Diagnóstico y Solicitud de Repuestos', detalle: 'Aceptación de orden y pedido a almacén' },
      { tiempo: '02:50', segundos: 170, titulo: 'Consultas con la IA (Tati)', detalle: 'Tickets activos por voz y reaperturas' },
      { tiempo: '03:30', segundos: 210, titulo: 'Pruebas Técnicas y Cierre', detalle: 'Registro de solución y fotos funcionales' }
    ]
  },
  SERVICIOS_GENERALES: {
    titulo: 'Rol Jefe de Servicios Generales (Mantenimiento)',
    descripcion: 'Supervisión de infraestructura física, asignación a cuadrillas de mantenimiento y reportes.',
    duracion: '3:40 min',
    video: '/videos/tutoriales/tutorial_servicios_generales.mp4',
    capitulos: [
      { tiempo: '00:00', segundos: 0, titulo: 'Consola de Mantenimiento', detalle: 'Matriz de requerimientos y menú por oficios' },
      { tiempo: '01:25', segundos: 85, titulo: 'Evaluación y Derivación a Auxiliar', detalle: 'Inspección de ambientes y asignación de orden' },
      { tiempo: '02:45', segundos: 165, titulo: 'Consultas con la IA (Tati)', detalle: 'Conteo de órdenes activas y navegación rápida' },
      { tiempo: '03:20', segundos: 200, titulo: 'Supervisión y Reporte Mensual', detalle: 'Validación de trabajos de infraestructura' }
    ]
  },
  AUXILIAR_SERVICIOS_GENERALES: {
    titulo: 'Rol Auxiliar de Mantenimiento',
    descripcion: 'Atención de averías en campo, fotogramas antes/después y reposición de materiales en almacén.',
    duracion: '3:40 min',
    video: '/videos/tutoriales/tutorial_auxiliar_servicios_generales.mp4',
    capitulos: [
      { tiempo: '00:00', segundos: 0, titulo: 'Órdenes de Trabajo y Menú', detalle: 'Recepción de requerimientos de infraestructura' },
      { tiempo: '01:25', segundos: 85, titulo: 'Fotograma de Respaldo y Reposición', detalle: 'Fotos antes/después y retiro de stock de almacén' },
      { tiempo: '02:45', segundos: 165, titulo: 'Consultas con la IA (Tati)', detalle: 'Consultar órdenes de mantenimiento por voz' },
      { tiempo: '03:20', segundos: 200, titulo: 'Cierre Técnico de la Orden', detalle: 'Informe de ejecución física terminada' }
    ]
  },
  DAF: {
    titulo: 'Rol DAF (Dirección de Asuntos Financieros)',
    descripcion: 'Control presupuestario, evaluación de cotizaciones y emisión de Certificación Presupuestaria.',
    duracion: '3:50 min',
    video: '/videos/tutoriales/tutorial_daf.mp4',
    capitulos: [
      { tiempo: '00:00', segundos: 0, titulo: 'Dashboard Financiero y Menú', detalle: 'Métricas de expedientes y menú de solicitudes' },
      { tiempo: '01:30', segundos: 90, titulo: 'Evaluación de Cotizaciones y Emisión', detalle: 'Revisión contable y emisión de certificación digital' },
      { tiempo: '02:50', segundos: 170, titulo: 'Consultas con la IA (Tati)', detalle: 'Orientación financiera y navegación con Tati' },
      { tiempo: '03:30', segundos: 210, titulo: 'Paso del Expediente a Tesorería', detalle: 'Firma y trazabilidad de fondos institucionales' }
    ]
  },
  JEFE_DAF: {
    titulo: 'Rol DAF (Dirección de Asuntos Financieros)',
    descripcion: 'Control presupuestario, evaluación de cotizaciones y emisión de Certificación Presupuestaria.',
    duracion: '3:50 min',
    video: '/videos/tutoriales/tutorial_daf.mp4',
    capitulos: [
      { tiempo: '00:00', segundos: 0, titulo: 'Dashboard Financiero y Menú', detalle: 'Métricas de expedientes y menú de solicitudes' },
      { tiempo: '01:30', segundos: 90, titulo: 'Evaluación de Cotizaciones y Emisión', detalle: 'Revisión contable y emisión de certificación digital' },
      { tiempo: '02:50', segundos: 170, titulo: 'Consultas con la IA (Tati)', detalle: 'Orientación financiera y navegación con Tati' },
      { tiempo: '03:30', segundos: 210, titulo: 'Paso del Expediente a Tesorería', detalle: 'Firma y trazabilidad de fondos institucionales' }
    ]
  },
  TESORERIA: {
    titulo: 'Rol Tesorería Institucional',
    descripcion: 'Verificación contable, registro de desembolsos en efectivo/banco y cierre de expedientes.',
    duracion: '3:35 min',
    video: '/videos/tutoriales/tutorial_tesoreria.mp4',
    capitulos: [
      { tiempo: '00:00', segundos: 0, titulo: 'Consola de Tesorería y Menú', detalle: 'Bandeja de expedientes con certificación DAF' },
      { tiempo: '01:25', segundos: 85, titulo: 'Registro de Desembolso y Comprobantes', detalle: 'Entrega de fondos, efectivo, transferencias y recibo' },
      { tiempo: '02:40', segundos: 160, titulo: 'Consultas con la IA (Tati)', detalle: 'Resumen de funciones y navegación por voz' },
      { tiempo: '03:15', segundos: 195, titulo: 'Archivo Contable Seguro', detalle: 'Cierre del asiento y descargo definitivo' }
    ]
  },
  ENCARGADO_COMPRAS_ALMACEN: {
    titulo: 'Rol Compras y Almacén',
    descripcion: 'Adquisición de insumos, registro en Kardex y emisión de Actas de Entrega físicas.',
    duracion: '3:45 min',
    video: '/videos/tutoriales/tutorial_almacen.mp4',
    capitulos: [
      { tiempo: '00:00', segundos: 0, titulo: 'Menú de Almacén y Compras', detalle: 'Requerimientos autorizados vs compras activas' },
      { tiempo: '01:30', segundos: 90, titulo: 'Kardex, Factura y Acta de Entrega', detalle: 'Ingreso a inventario y acta de entrega firmada' },
      { tiempo: '02:50', segundos: 170, titulo: 'Consultas con la IA (Tati)', detalle: 'Estado de compras y avisos por voz' },
      { tiempo: '03:30', segundos: 210, titulo: 'Conclusión del Suministro', detalle: 'Descuento de stock y archivo logístico' }
    ]
  },
  ADMIN: {
    titulo: 'Rol Administración y Dirección',
    descripcion: 'Visto bueno de compras, gestión de usuarios, roles, auditoría y bitácora del sistema.',
    duracion: '3:50 min',
    video: '/videos/tutoriales/tutorial_admin.mp4',
    capitulos: [
      { tiempo: '00:00', segundos: 0, titulo: 'Panel Administrativo y Menú', detalle: 'Consola general de Dirección y Superusuario' },
      { tiempo: '01:30', segundos: 90, titulo: 'Visto Bueno de Gastos y RBAC', detalle: 'Aprobaciones de Dirección y roles de usuarios' },
      { tiempo: '02:50', segundos: 170, titulo: 'Consultas con la IA (Tati)', detalle: 'Resumen de módulos con Tati' },
      { tiempo: '03:30', segundos: 210, titulo: 'Auditoría Forense y Bitácora', detalle: 'Trazabilidad de eventos y cierre seguro' }
    ]
  }
}

const datosRolActual = computed(() => {
  return CATALOGO_ROLES[rolActivo.value] || CATALOGO_ROLES.SOLICITANTE
})

/* ============================================================
   ACCIONES DEL MODAL Y REPRODUCTOR
   ============================================================ */
function toggleModal() {
  modalAbierto.value = !modalAbierto.value
  mostrarTooltip.value = false
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

function saltarATiempo(segundos) {
  if (videoRef.value) {
    videoRef.value.currentTime = segundos
    videoRef.value.play().catch(() => {})
  }
}

function onVideoPlay() {}
function onVideoPause() {}

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
  sessionTimer = setInterval(actualizarSesion, 1000)
  evaluarTooltip()
})

onUnmounted(() => {
  window.removeEventListener('storage', actualizarSesion)
  if (sessionTimer) clearInterval(sessionTimer)
})
</script>

<style scoped>
/* ============================================================
   BOTÓN FLOTANTE (FAB) — IDENTIDAD INSTITUCIONAL EMI / SIA
   Idéntico en tamaño, degradado, borde y elevación a Tati
   ============================================================ */
.sia-tutorial-contenedor {
  position: relative;
  font-family: inherit;
}

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
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 22px rgba(12, 42, 79, 0.45);
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
  outline: none;
}

.sia-tutorial-fab:hover {
  transform: scale(1.08);
  box-shadow: 0 8px 28px rgba(12, 42, 79, 0.65);
  border-color: #FFC72C;
}

.sia-tutorial-fab--activo {
  border-color: #FFC72C;
  box-shadow: 0 4px 18px rgba(12, 42, 79, 0.5);
  transform: scale(0.96);
}

.sia-tutorial-fab__badge {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #FFC72C;
  color: #0C2A4F;
  border: 2px solid #0C2A4F;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

/* Tooltip informativo inicial */
.sia-tutorial-tooltip {
  position: fixed;
  bottom: 96px;
  right: 96px;
  z-index: 999997;
  background: #0C2A4F;
  color: #FFFFFF;
  border: 1px solid rgba(255, 199, 44, 0.5);
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  max-width: 280px;
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
  50% { transform: translateY(-5px); }
}

/* ============================================================
   MODAL DE VIDEO — DISEÑO CINE / INSTITUCIONAL EMI
   ============================================================ */
.sia-tutorial-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(12, 42, 79, 0.78);
  backdrop-filter: blur(6px);
  z-index: 1000000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}

.sia-tutorial-modal {
  background: #FFFFFF;
  width: 100%;
  max-width: 1040px;
  max-height: 90vh;
  border-radius: 20px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
  border: 1px solid #D7E3EF;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: scaleIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

/* Cabecera del modal */
.sia-tutorial-modal__header {
  background: linear-gradient(135deg, #0C2A4F 0%, #173E6D 100%);
  color: #FFFFFF;
  padding: 18px 24px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  border-bottom: 3px solid #FFC72C;
}

.sia-tutorial-modal__insignia {
  display: inline-block;
  background: rgba(255, 199, 44, 0.2);
  color: #FFC72C;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
  letter-spacing: 0.8px;
  margin-bottom: 6px;
}

.sia-tutorial-modal__titulo {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #FFFFFF;
}

.sia-tutorial-modal__subtitulo {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: #D3E0EA;
}

.sia-tutorial-modal__btn-cerrar {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.2s ease;
}

.sia-tutorial-modal__btn-cerrar:hover {
  background: rgba(255, 199, 44, 0.3);
  color: #FFC72C;
  border-color: #FFC72C;
}

/* Cuerpo del modal */
.sia-tutorial-modal__cuerpo {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 20px;
  padding: 20px 24px;
  overflow-y: auto;
  max-height: calc(90vh - 170px);
}

.sia-tutorial-video-wrapper {
  background: #000000;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
  aspect-ratio: 16 / 9;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sia-tutorial-video {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

/* Tarjetas informativas de calidad */
.sia-tutorial-info-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 14px;
  padding: 12px 16px;
  background: #F4F7FB;
  border-radius: 10px;
  border: 1px solid #E1E8F0;
}

.sia-tutorial-info-card__label {
  font-size: 12px;
  color: #5C7084;
  margin-right: 4px;
}

.sia-tutorial-info-card__valor {
  font-size: 12px;
  font-weight: 600;
  color: #0C2A4F;
}

/* Columna de Capítulos */
.sia-tutorial-capitulos__titulo {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 700;
  color: #0C2A4F;
  border-bottom: 2px solid #E9EFF6;
  padding-bottom: 8px;
}

.sia-tutorial-capitulos__lista {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sia-tutorial-capitulo-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 12px;
  background: #F8FAFD;
  border: 1px solid #E5ECF3;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sia-tutorial-capitulo-item:hover {
  background: #EDF3FA;
  border-color: #0C2A4F;
  transform: translateX(3px);
}

.sia-tutorial-capitulo__tiempo {
  background: #0C2A4F;
  color: #FFC72C;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 6px;
  border-radius: 6px;
  flex-shrink: 0;
}

.sia-tutorial-capitulo__textos strong {
  display: block;
  font-size: 13px;
  color: #0C2A4F;
  line-height: 1.3;
}

.sia-tutorial-capitulo__textos small {
  display: block;
  font-size: 11px;
  color: #6A8197;
  margin-top: 2px;
}

/* Banner de Tati */
.sia-tutorial-asistente-banner {
  margin-top: 14px;
  background: linear-gradient(135deg, #EDF4FC 0%, #E3EDF9 100%);
  border: 1px solid #B8D3EE;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.sia-tutorial-asistente-banner__icono {
  font-size: 26px;
}

.sia-tutorial-asistente-banner__texto strong {
  font-size: 12px;
  color: #0C2A4F;
  display: block;
}

.sia-tutorial-asistente-banner__texto p {
  margin: 2px 0 0 0;
  font-size: 11px;
  color: #385775;
  line-height: 1.35;
}

/* Pie del modal */
.sia-tutorial-modal__footer {
  background: #F4F7FB;
  border-top: 1px solid #E1E8F0;
  padding: 14px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sia-tutorial-modal__nota {
  font-size: 12px;
  color: #6C8299;
}

.sia-tutorial-btn-entendido {
  background: #0C2A4F;
  color: #FFFFFF;
  border: none;
  padding: 9px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.sia-tutorial-btn-entendido:hover {
  background: #173E6D;
}

/* Transiciones */
.sia-modal-fade-enter-active,
.sia-modal-fade-leave-active {
  transition: opacity 0.22s ease;
}

.sia-modal-fade-enter-from,
.sia-modal-fade-leave-to {
  opacity: 0;
}

@media (max-width: 860px) {
  .sia-tutorial-modal__cuerpo {
    grid-template-columns: 1fr;
  }
  .sia-tutorial-fab {
    right: 80px !important;
  }
}
</style>
