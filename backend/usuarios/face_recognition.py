"""
Servicio de reconocimiento facial usando OpenCV YuNet + SFace.

YuNet: Detector de rostros rápido y preciso
SFace: Extractor de embeddings de 128 dimensiones

No almacena imágenes, solo embeddings (512 bytes por usuario).

Umbral de similitud coseno: 0.363 (recomendado por SFace)
- >= 0.363: Misma persona
- < 0.363: Personas diferentes

Requiere modelos ONNX en backend/models/:
- face_detection_yunet_2023mar.onnx
- face_recognition_sface_2021dec.onnx

Descargar de: https://github.com/opencv/opencv_zoo
"""

import base64
import os
from pathlib import Path

import cv2
import numpy as np

from django.conf import settings


# ==========================================================
# RUTAS DE MODELOS
# ==========================================================

MODELS_DIR = Path(settings.BASE_DIR) / "models"

YUNET_MODEL = MODELS_DIR / "face_detection_yunet_2023mar.onnx"
SFACE_MODEL = MODELS_DIR / "face_recognition_sface_2021dec.onnx"


# ==========================================================
# SERVICIO DE RECONOCIMIENTO FACIAL
# ==========================================================

class FaceRecognitionService:
    """
    Servicio singleton para reconocimiento facial.

    Carga los modelos de forma lazy (primera vez que se usan).
    """

    _detector = None
    _recognizer = None
    _initialized = False

    # Umbral de similitud coseno (recomendado por SFace)
    COSINE_THRESHOLD = 0.363

    # Umbral para detectar foto estática (demasiado similar)
    STATIC_THRESHOLD = 0.995


    @classmethod
    def _init_models(cls):
        """Inicializa los modelos de detección y reconocimiento."""

        if cls._initialized:
            return True, ""

        # Verificar que existen los modelos
        if not YUNET_MODEL.exists():
            return False, (
                f"Modelo YuNet no encontrado en {YUNET_MODEL}. "
                "Descargue de https://github.com/opencv/opencv_zoo"
            )

        if not SFACE_MODEL.exists():
            return False, (
                f"Modelo SFace no encontrado en {SFACE_MODEL}. "
                "Descargue de https://github.com/opencv/opencv_zoo"
            )

        try:
            # Detector de rostros YuNet
            # score_threshold 0.8: balance entre detectar rostros y evitar falsos positivos
            cls._detector = cv2.FaceDetectorYN.create(
                str(YUNET_MODEL),
                "",
                (320, 320),
                score_threshold=0.8,
                nms_threshold=0.3,
                top_k=5000
            )

            # Reconocedor facial SFace
            cls._recognizer = cv2.FaceRecognizerSF.create(
                str(SFACE_MODEL),
                ""
            )

            cls._initialized = True
            return True, ""

        except Exception as e:
            return False, f"Error al cargar modelos: {str(e)}"


    @classmethod
    def _decode_image(cls, image_base64: str):
        """
        Decodifica imagen base64 a array OpenCV.

        Args:
            image_base64: String base64 (puede incluir prefijo data:image/...)

        Returns:
            Tuple (imagen_cv2, error_message)
        """
        try:
            # Remover prefijo data:image/...;base64, si existe
            if "," in image_base64:
                image_base64 = image_base64.split(",", 1)[1]

            # Decodificar base64
            img_data = base64.b64decode(image_base64)

            # Convertir a array numpy
            img_array = np.frombuffer(img_data, dtype=np.uint8)

            # Decodificar imagen
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if img is None:
                return None, "No se pudo decodificar la imagen."

            return img, ""

        except Exception as e:
            return None, f"Error al procesar imagen: {str(e)}"


    @classmethod
    def extract_embedding(
        cls,
        image_base64: str
    ) -> tuple:
        """
        Extrae el embedding facial de una imagen.

        Args:
            image_base64: Imagen en formato base64

        Returns:
            Tuple (embedding_array | None, error_message)
            - embedding_array: numpy array de 128 floats
            - error_message: string vacío si OK, mensaje de error si falló
        """

        # Inicializar modelos
        ok, error = cls._init_models()
        if not ok:
            return None, error

        # Decodificar imagen
        img, error = cls._decode_image(image_base64)
        if img is None:
            return None, error

        # Configurar tamaño del detector
        height, width = img.shape[:2]
        cls._detector.setInputSize((width, height))

        # Detectar rostros
        _, faces = cls._detector.detect(img)

        if faces is None or len(faces) == 0:
            return None, "No se detectó ningún rostro en la imagen."

        # Si hay múltiples rostros, tomar el más grande (ignora falsos positivos pequeños)
        if len(faces) > 1:
            # Ordenar por área del bounding box (w * h), índices 2 y 3
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)

            # Verificar que el rostro más grande sea significativamente mayor
            area_mayor = faces[0][2] * faces[0][3]
            area_segundo = faces[1][2] * faces[1][3]

            # Si el segundo rostro es más del 70% del tamaño del primero,
            # probablemente hay dos personas reales (muy similares en tamaño)
            if area_segundo > area_mayor * 0.7:
                return None, "Se detectó más de un rostro prominente. Asegúrese de estar solo."

        # Alinear rostro y extraer embedding (usar el rostro más grande)
        face = faces[0]
        aligned = cls._recognizer.alignCrop(img, face)
        embedding = cls._recognizer.feature(aligned)

        return embedding.flatten(), ""


    @classmethod
    def compare_embeddings(
        cls,
        stored: bytes,
        captured: np.ndarray,
        threshold: float = None
    ) -> tuple:
        """
        Compara un embedding almacenado con uno capturado.

        Args:
            stored: Embedding almacenado como bytes
            captured: Embedding capturado como numpy array
            threshold: Umbral de similitud (default: 0.363)

        Returns:
            Tuple (is_match, similarity_score)
        """

        if threshold is None:
            threshold = cls.COSINE_THRESHOLD

        # Inicializar modelos si no están
        ok, _ = cls._init_models()
        if not ok:
            return False, 0.0

        # Convertir bytes a array
        stored_arr = np.frombuffer(stored, dtype=np.float32)

        # Calcular similitud coseno
        score = cls._recognizer.match(
            stored_arr.reshape(1, -1),
            captured.reshape(1, -1),
            cv2.FaceRecognizerSF_FR_COSINE
        )

        return score >= threshold, float(score)


    @classmethod
    def validate_liveness(
        cls,
        frames_base64: list
    ) -> tuple:
        """
        Valida prueba de vida analizando múltiples frames.

        Verifica que:
        1. Todos los frames tienen exactamente un rostro
        2. Todos los rostros son de la misma persona (alta similitud)
        3. Los frames no son idénticos (no es una foto estática)

        Args:
            frames_base64: Lista de 3-5 imágenes en base64

        Returns:
            Tuple (is_live, error_message)
        """

        if len(frames_base64) < 3:
            return False, "Se requieren al menos 3 capturas para validar."

        if len(frames_base64) > 5:
            frames_base64 = frames_base64[:5]

        # Extraer embeddings de todos los frames
        embeddings = []

        for i, frame in enumerate(frames_base64):
            emb, error = cls.extract_embedding(frame)

            if emb is None:
                return False, f"Captura {i + 1}: {error}"

            embeddings.append(emb)

        # Verificar que todos son la misma persona
        # pero no son frames idénticos (foto estática)
        base_emb = embeddings[0]

        for i, emb in enumerate(embeddings[1:], start=2):

            # Inicializar modelos para usar match
            cls._init_models()

            score = cls._recognizer.match(
                base_emb.reshape(1, -1),
                emb.reshape(1, -1),
                cv2.FaceRecognizerSF_FR_COSINE
            )

            # Debe ser la misma persona
            if score < cls.COSINE_THRESHOLD:
                return False, (
                    "Las capturas no corresponden a la misma persona."
                )

            # No debe ser una foto estática
            if score > cls.STATIC_THRESHOLD:
                return False, (
                    "Las capturas son demasiado similares. "
                    "Por favor, muévase naturalmente."
                )

        return True, ""


    @classmethod
    def embedding_to_bytes(cls, embedding: np.ndarray) -> bytes:
        """Convierte embedding numpy a bytes para almacenar en BD."""
        return embedding.astype(np.float32).tobytes()


    @classmethod
    def bytes_to_embedding(cls, data: bytes) -> np.ndarray:
        """Convierte bytes de BD a embedding numpy."""
        return np.frombuffer(data, dtype=np.float32)
