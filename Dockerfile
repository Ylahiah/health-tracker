FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Pre-download YOLOv8n model to avoid downloading it at runtime every time
# We run a python one-liner to trigger the download
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

COPY . .

EXPOSE 8080

CMD ["streamlit", "run", "app/main.py", "--server.port=8080", "--server.address=0.0.0.0"]
