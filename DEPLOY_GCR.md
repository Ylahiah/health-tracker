# Guía de Despliegue en Google Cloud Run 🚀 (Actualizado IA)

Esta guía te ayudará a desplegar tu aplicación en Google Cloud Run, ahora con soporte para **Vision AI** (YOLOv8).

## Prerrequisitos

1.  Cuenta de Google Cloud Platform (GCP).
2.  `gcloud` CLI instalado y autenticado.
3.  Docker instalado.

## Cambios Importantes para IA

La nueva versión incluye bibliotecas pesadas como `ultralytics` y `opencv`. El `Dockerfile` ya está optimizado para:
- Instalar dependencias del sistema (`libgl1`).
- Pre-descargar el modelo `yolov8n.pt` durante la construcción de la imagen (para que no falle en tiempo de ejecución ni tarde demasiado al arrancar).

## Pasos de Despliegue

### 1. Configuración del Proyecto

```bash
gcloud config set project TU_PROYECTO_ID
```

### 2. Construir la Imagen (Con Cloud Build)

Recomendamos usar Cloud Build para no sobrecargar tu máquina local y aprovechar el caché de Google.

```bash
gcloud builds submit --tag gcr.io/TU_PROYECTO_ID/health-tracker-ai
```

*Nota: Esto puede tardar unos minutos más que antes debido a las nuevas librerías.*

### 3. Despliegue en Cloud Run

Necesitamos aumentar un poco la memoria debido al modelo de IA. Recomendamos al menos **1GB o 2GB de RAM**.

```bash
gcloud run deploy health-tracker-ai \
  --image gcr.io/TU_PROYECTO_ID/health-tracker-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --set-secrets="/app/.streamlit/secrets.toml=streamlit-secrets:latest"
```

*   `--memory 2Gi`: Asigna 2GB de RAM (YOLO puede ser exigente).
*   `--cpu 2`: Asigna 2 vCPUs para una inferencia más rápida.

### 4. Verificar

Abre la URL que te proporciona el comando. Ve a la pestaña **Nutrición** y prueba subir una foto de una manzana o un sándwich.

## Solución de Problemas Comunes

- **Error de Memoria**: Si la app se reinicia al subir una foto, aumenta la memoria a `4Gi`.
- **Error de OpenCV**: Si ves errores sobre `libGL.so`, asegúrate de que el `Dockerfile` tenga las líneas de `apt-get install libgl1`. (Ya incluidas en esta versión).
