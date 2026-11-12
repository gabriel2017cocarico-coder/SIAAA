"""
Endpoints de autenticación facial (2FA).

POST /api/usuarios/face-register/   — Registrar rostro (auth required)
POST /api/usuarios/face-verify/     — Verificar rostro (2FA step)
DELETE /api/usuarios/face-disable/  — Deshabilitar 2FA facial
GET /api/usuarios/face-status/      — Estado del 2FA facial
"""

import secrets
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from auditoria.utils import registrar_bitacora
from .authentication import ExpiringTokenAuthentication
from .models import Usuario, UsuarioRol
from .face_recognition import FaceRecognitionService
from .views import obtener_permisos_usuario


# ==========================================================
# REGISTRAR ROSTRO
# ==========================================================

@api_view(["POST"])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAuthenticated])
def face_register(request):
    """
    Registra el rostro del usuario autenticado.

    Requiere 3-5 capturas para validar prueba de vida.
    Solo almacena el embedding (128 floats = 512 bytes).

    Body:
        {
            "frames": [
                "data:image/jpeg;base64,...",
                "data:image/jpeg;base64,...",
                "data:image/jpeg;base64,..."
            ]
        }

    Response OK:
        { "ok": true, "mensaje": "Rostro registrado correctamente." }

    Response Error:
        { "ok": false, "mensaje": "..." }
    """

    usuario = request.user
    frames = request.data.get("frames", [])

    # ------------------------------------------------------
    # VALIDAR CANTIDAD DE FRAMES
    # ------------------------------------------------------

    if not frames or len(frames) < 3:
        return Response(
            {
                "ok": False,
                "mensaje": "Se requieren al menos 3 capturas."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(frames) > 5:
        frames = frames[:5]

    # ------------------------------------------------------
    # VALIDAR PRUEBA DE VIDA
    # ------------------------------------------------------

    is_live, error = FaceRecognitionService.validate_liveness(frames)

    if not is_live:
        registrar_bitacora(
            request=request,
            usuario=usuario,
            accion="FACE_REGISTER_LIVENESS_FAIL",
            modulo="Autenticación",
            detalle=f"Prueba de vida fallida: {error}",
            nivel="SECURITY"
        )

        return Response(
            {
                "ok": False,
                "mensaje": error
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ------------------------------------------------------
    # EXTRAER EMBEDDING
    # ------------------------------------------------------

    # Usar el frame del medio (mejor calidad típicamente)
    middle_frame = frames[len(frames) // 2]
    embedding, error = FaceRecognitionService.extract_embedding(middle_frame)

    if embedding is None:
        return Response(
            {
                "ok": False,
                "mensaje": error
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ------------------------------------------------------
    # GUARDAR EMBEDDING (NO LA IMAGEN)
    # ------------------------------------------------------

    usuario.face_embedding = FaceRecognitionService.embedding_to_bytes(embedding)
    usuario.face_registered_at = timezone.now()
    usuario.face_2fa_enabled = True
    usuario.failed_face_attempts = 0
    usuario.face_locked_until = None

    usuario.save(
        update_fields=[
            "face_embedding",
            "face_registered_at",
            "face_2fa_enabled",
            "failed_face_attempts",
            "face_locked_until"
        ]
    )

    registrar_bitacora(
        request=request,
        usuario=usuario,
        accion="FACE_REGISTER_OK",
        modulo="Autenticación",
        detalle="Rostro registrado exitosamente para 2FA.",
        nivel="INFO"
    )

    return Response({
        "ok": True,
        "mensaje": "Rostro registrado correctamente."
    })


# ==========================================================
# VERIFICAR ROSTRO (2FA)
# ==========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def face_verify(request):
    """
    Segundo paso del login: verificar rostro.

    Requiere face_token del paso 1 (password OK).

    Body:
        {
            "face_token": "...",
            "frames": [...]
        }

    Response OK:
        {
            "ok": true,
            "token": "...",
            "usuario": { ... }
        }

    Response Error:
        { "ok": false, "mensaje": "..." }
    """

    face_token = request.data.get("face_token", "")
    frames = request.data.get("frames", [])

    # ------------------------------------------------------
    # VALIDAR TOKEN
    # ------------------------------------------------------

    if not face_token:
        return Response(
            {
                "ok": False,
                "mensaje": "Token facial requerido."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ------------------------------------------------------
    # RECUPERAR SESIÓN PENDIENTE
    # ------------------------------------------------------

    cache_key = f"face_2fa_{face_token}"
    pending = cache.get(cache_key)

    if not pending:
        return Response(
            {
                "ok": False,
                "mensaje": "Sesión expirada. Inicie sesión de nuevo."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # ------------------------------------------------------
    # BUSCAR USUARIO
    # ------------------------------------------------------

    try:
        usuario = Usuario.objects.get(pk=pending["user_id"])
    except Usuario.DoesNotExist:
        cache.delete(cache_key)
        return Response(
            {
                "ok": False,
                "mensaje": "Usuario no encontrado."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # ------------------------------------------------------
    # VERIFICAR BLOQUEO FACIAL
    # ------------------------------------------------------

    if (
        usuario.face_locked_until
        and usuario.face_locked_until > timezone.now()
    ):
        minutos_restantes = int(
            (usuario.face_locked_until - timezone.now()).total_seconds() / 60
        ) + 1

        return Response(
            {
                "ok": False,
                "mensaje": (
                    f"Verificación facial bloqueada. "
                    f"Intente en {minutos_restantes} minutos."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # ------------------------------------------------------
    # VALIDAR FRAMES
    # ------------------------------------------------------

    if not frames or len(frames) < 3:
        return Response(
            {
                "ok": False,
                "mensaje": "Se requieren al menos 3 capturas."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ------------------------------------------------------
    # VALIDAR PRUEBA DE VIDA
    # ------------------------------------------------------

    is_live, error = FaceRecognitionService.validate_liveness(frames)

    if not is_live:
        _incrementar_intentos_fallidos(request, usuario, "LIVENESS_FAIL", error)
        cache.delete(cache_key)

        return Response(
            {
                "ok": False,
                "mensaje": error
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ------------------------------------------------------
    # EXTRAER Y COMPARAR EMBEDDING
    # ------------------------------------------------------

    middle_frame = frames[len(frames) // 2]
    embedding, error = FaceRecognitionService.extract_embedding(middle_frame)

    if embedding is None:
        return Response(
            {
                "ok": False,
                "mensaje": error
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Comparar con el embedding guardado
    match, score = FaceRecognitionService.compare_embeddings(
        usuario.face_embedding,
        embedding
    )

    if not match:
        blocked = _incrementar_intentos_fallidos(
            request,
            usuario,
            "MISMATCH",
            f"Similitud: {score:.3f}"
        )
        cache.delete(cache_key)

        if blocked:
            return Response(
                {
                    "ok": False,
                    "mensaje": (
                        "Verificación facial bloqueada temporalmente "
                        "por múltiples intentos fallidos."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            {
                "ok": False,
                "mensaje": "El rostro no coincide con el registrado."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # ------------------------------------------------------
    # VERIFICACIÓN EXITOSA
    # ------------------------------------------------------

    cache.delete(cache_key)

    # Resetear contadores
    usuario.failed_face_attempts = 0
    usuario.face_locked_until = None
    usuario.save(
        update_fields=[
            "failed_face_attempts",
            "face_locked_until"
        ]
    )

    # Crear o refrescar token de autenticación
    token, _ = Token.objects.get_or_create(user=usuario)

    horas = getattr(settings, "SESION_TOKEN_HORAS_VALIDEZ", 12)
    if timezone.now() > token.created + timedelta(hours=horas):
        token.delete()
        token = Token.objects.create(user=usuario)

    registrar_bitacora(
        request=request,
        usuario=usuario,
        accion="FACE_VERIFY_OK",
        modulo="Autenticación",
        detalle=f"Verificación facial exitosa. Similitud: {score:.3f}",
        nivel="INFO"
    )

    # Retornar misma estructura que login_view
    return Response({
        "ok": True,
        "token": token.key,
        "usuario": pending["usuario_data"]
    })


def _incrementar_intentos_fallidos(request, usuario, tipo, detalle):
    """
    Incrementa contador de intentos fallidos.
    Bloquea si excede el límite.

    Returns:
        bool: True si se bloqueó la cuenta
    """

    usuario.failed_face_attempts += 1
    blocked = False

    max_intentos = getattr(settings, "FACE_2FA_MAX_INTENTOS", 3)
    minutos_bloqueo = getattr(settings, "FACE_2FA_MINUTOS_BLOQUEO", 30)

    if usuario.failed_face_attempts >= max_intentos:
        usuario.face_locked_until = timezone.now() + timedelta(
            minutes=minutos_bloqueo
        )
        usuario.failed_face_attempts = 0
        blocked = True

        registrar_bitacora(
            request=request,
            usuario=usuario,
            accion="FACE_VERIFY_BLOCKED",
            modulo="Autenticación",
            detalle=f"Bloqueado por {max_intentos} intentos fallidos. {detalle}",
            nivel="SECURITY"
        )
    else:
        registrar_bitacora(
            request=request,
            usuario=usuario,
            accion=f"FACE_VERIFY_{tipo}",
            modulo="Autenticación",
            detalle=f"Intento {usuario.failed_face_attempts}/{max_intentos}. {detalle}",
            nivel="SECURITY"
        )

    usuario.save(
        update_fields=[
            "failed_face_attempts",
            "face_locked_until"
        ]
    )

    return blocked


# ==========================================================
# DESHABILITAR 2FA FACIAL
# ==========================================================

@api_view(["DELETE"])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAuthenticated])
def face_disable(request):
    """
    Deshabilita 2FA facial y elimina el embedding.

    Response OK:
        { "ok": true, "mensaje": "2FA facial deshabilitado." }
    """

    usuario = request.user

    if not usuario.face_2fa_enabled:
        return Response(
            {
                "ok": False,
                "mensaje": "2FA facial no está habilitado."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    usuario.face_embedding = None
    usuario.face_registered_at = None
    usuario.face_2fa_enabled = False
    usuario.failed_face_attempts = 0
    usuario.face_locked_until = None

    usuario.save(
        update_fields=[
            "face_embedding",
            "face_registered_at",
            "face_2fa_enabled",
            "failed_face_attempts",
            "face_locked_until"
        ]
    )

    registrar_bitacora(
        request=request,
        usuario=usuario,
        accion="FACE_2FA_DISABLED",
        modulo="Autenticación",
        detalle="Usuario deshabilitó 2FA facial.",
        nivel="INFO"
    )

    return Response({
        "ok": True,
        "mensaje": "2FA facial deshabilitado."
    })


# ==========================================================
# ESTADO DEL 2FA FACIAL
# ==========================================================

@api_view(["GET"])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAuthenticated])
def face_status(request):
    """
    Retorna el estado del 2FA facial del usuario.

    Response:
        {
            "ok": true,
            "face_2fa_enabled": true,
            "face_registered_at": "2024-01-15T10:30:00Z"
        }
    """

    usuario = request.user

    return Response({
        "ok": True,
        "face_2fa_enabled": usuario.face_2fa_enabled,
        "face_registered_at": (
            usuario.face_registered_at.isoformat()
            if usuario.face_registered_at
            else None
        )
    })


# ==========================================================
# LOGIN CON RECONOCIMIENTO FACIAL (SIN CONTRASEÑA)
# ==========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def face_login(request):
    """
    Login directo con reconocimiento facial (sin contraseña).

    Requiere que el usuario tenga 2FA facial habilitado previamente.

    Body:
        {
            "email": "usuario@emi.edu.bo",
            "frames": [...]
        }

    Response OK:
        {
            "ok": true,
            "token": "...",
            "usuario": { ... }
        }
    """

    email = request.data.get("email", "").strip().lower()
    frames = request.data.get("frames", [])

    # ------------------------------------------------------
    # VALIDAR EMAIL
    # ------------------------------------------------------

    if not email:
        return Response(
            {
                "ok": False,
                "mensaje": "Ingrese su correo institucional."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ------------------------------------------------------
    # BUSCAR USUARIO
    # ------------------------------------------------------

    try:
        usuario = Usuario.objects.get(email__iexact=email)
    except Usuario.DoesNotExist:
        return Response(
            {
                "ok": False,
                "mensaje": "Usuario no encontrado."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # ------------------------------------------------------
    # VERIFICAR USUARIO ACTIVO
    # ------------------------------------------------------

    if not usuario.is_active:
        registrar_bitacora(
            request=request,
            usuario=usuario,
            accion="FACE_LOGIN_USUARIO_INACTIVO",
            modulo="Autenticación",
            detalle="Intento de login facial con usuario inactivo.",
            nivel="SECURITY"
        )
        return Response(
            {
                "ok": False,
                "mensaje": "Usuario inactivo."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # ------------------------------------------------------
    # VERIFICAR QUE TENGA 2FA FACIAL HABILITADO
    # ------------------------------------------------------

    if not usuario.face_2fa_enabled or not usuario.face_embedding:
        return Response(
            {
                "ok": False,
                "mensaje": "Este usuario no tiene reconocimiento facial habilitado."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ------------------------------------------------------
    # VERIFICAR BLOQUEO FACIAL
    # ------------------------------------------------------

    if (
        usuario.face_locked_until
        and usuario.face_locked_until > timezone.now()
    ):
        minutos_restantes = int(
            (usuario.face_locked_until - timezone.now()).total_seconds() / 60
        ) + 1

        return Response(
            {
                "ok": False,
                "mensaje": (
                    f"Verificación facial bloqueada. "
                    f"Intente en {minutos_restantes} minutos."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # ------------------------------------------------------
    # VERIFICAR BLOQUEO POR CONTRASEÑA
    # ------------------------------------------------------

    if (
        usuario.locked_until
        and usuario.locked_until > timezone.now()
    ):
        return Response(
            {
                "ok": False,
                "mensaje": "Cuenta bloqueada temporalmente."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # ------------------------------------------------------
    # VALIDAR FRAMES
    # ------------------------------------------------------

    if not frames or len(frames) < 3:
        return Response(
            {
                "ok": False,
                "mensaje": "Se requieren al menos 3 capturas."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ------------------------------------------------------
    # VALIDAR PRUEBA DE VIDA
    # ------------------------------------------------------

    is_live, error = FaceRecognitionService.validate_liveness(frames)

    if not is_live:
        _incrementar_intentos_fallidos(request, usuario, "LIVENESS_FAIL", error)

        return Response(
            {
                "ok": False,
                "mensaje": error
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ------------------------------------------------------
    # EXTRAER Y COMPARAR EMBEDDING
    # ------------------------------------------------------

    middle_frame = frames[len(frames) // 2]
    embedding, error = FaceRecognitionService.extract_embedding(middle_frame)

    if embedding is None:
        return Response(
            {
                "ok": False,
                "mensaje": error
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Comparar con el embedding guardado
    match, score = FaceRecognitionService.compare_embeddings(
        usuario.face_embedding,
        embedding
    )

    if not match:
        blocked = _incrementar_intentos_fallidos(
            request,
            usuario,
            "FACE_LOGIN_MISMATCH",
            f"Similitud: {score:.3f}"
        )

        if blocked:
            return Response(
                {
                    "ok": False,
                    "mensaje": (
                        "Verificación facial bloqueada temporalmente "
                        "por múltiples intentos fallidos."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            {
                "ok": False,
                "mensaje": "El rostro no coincide con el registrado."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # ------------------------------------------------------
    # LOGIN EXITOSO
    # ------------------------------------------------------

    # Resetear contadores
    usuario.failed_face_attempts = 0
    usuario.face_locked_until = None
    usuario.failed_attempts = 0
    usuario.locked_until = None
    usuario.save(
        update_fields=[
            "failed_face_attempts",
            "face_locked_until",
            "failed_attempts",
            "locked_until"
        ]
    )

    # Crear o refrescar token
    token, _ = Token.objects.get_or_create(user=usuario)

    horas = getattr(settings, "SESION_TOKEN_HORAS_VALIDEZ", 12)
    if timezone.now() > token.created + timedelta(hours=horas):
        token.delete()
        token = Token.objects.create(user=usuario)

    # Obtener roles
    roles = []
    asignaciones = (
        UsuarioRol.objects
        .filter(usuario=usuario, activo=True, rol__activo=True)
        .select_related("rol", "area")
        .order_by("rol__nombre")
    )

    for asignacion in asignaciones:
        roles.append({
            "id": asignacion.id,
            "rol_id": asignacion.rol.id,
            "codigo": asignacion.rol.codigo,
            "rol_codigo": asignacion.rol.codigo,
            "nombre": asignacion.rol.nombre,
            "rol_nombre": asignacion.rol.nombre,
            "es_global": asignacion.rol.es_global,
            "area_id": asignacion.area.id if asignacion.area else None,
            "area": asignacion.area.nombre if asignacion.area else None,
            "area_codigo": asignacion.area.codigo if asignacion.area else None,
            "area_nombre": asignacion.area.nombre if asignacion.area else None,
        })

    # Obtener permisos
    permisos = obtener_permisos_usuario(usuario)

    registrar_bitacora(
        request=request,
        usuario=usuario,
        accion="FACE_LOGIN_OK",
        modulo="Autenticación",
        detalle=f"Login facial exitoso. Similitud: {score:.3f}",
        nivel="INFO"
    )

    return Response({
        "ok": True,
        "token": token.key,
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre_completo,
            "nombre_completo": usuario.nombre_completo,
            "email": usuario.email,
            "must_change_password": usuario.must_change_password,
            "roles": roles,
            "permisos": permisos,
        }
    })
