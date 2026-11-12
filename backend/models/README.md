# Modelos ONNX para Reconocimiento Facial

Este directorio debe contener los modelos de OpenCV para detección y reconocimiento facial.

## Modelos Requeridos

1. **YuNet** (Detector de rostros)
   - Archivo: `face_detection_yunet_2023mar.onnx`
   - Función: Detecta rostros en imágenes

2. **SFace** (Extractor de embeddings)
   - Archivo: `face_recognition_sface_2021dec.onnx`
   - Función: Extrae embeddings de 128 dimensiones para comparación

## Descarga

Los modelos están disponibles en el repositorio oficial de OpenCV Zoo:

**YuNet:**
```
https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
```

**SFace:**
```
https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx
```

## Descarga Rápida (PowerShell)

```powershell
cd backend/models

# YuNet
Invoke-WebRequest -Uri "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx" -OutFile "face_detection_yunet_2023mar.onnx"

# SFace
Invoke-WebRequest -Uri "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx" -OutFile "face_recognition_sface_2021dec.onnx"
```

## Verificación

Después de descargar, el directorio debe contener:
```
backend/models/
├── face_detection_yunet_2023mar.onnx    (~439 KB)
├── face_recognition_sface_2021dec.onnx  (~37 MB)
└── README.md
```

## Notas

- Estos modelos NO contienen datos personales
- Son modelos pre-entrenados para uso general
- No requieren entrenamiento adicional
- Compatibles con OpenCV 4.8+
