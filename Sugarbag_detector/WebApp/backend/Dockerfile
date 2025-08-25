# Используем официальный Python 3.11 slim образ
FROM python:3.11-slim
RUN pip install opencv-python-headless
# Устанавливаем зависимости для сборки и OpenCV
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip
RUN python -m pip install --upgrade pip

# Создаём рабочую директорию
WORKDIR /app

# Копируем requirements.txt (если есть)
COPY requirements.txt .

# Устанавливаем Python-зависимости (если requirements.txt существует)
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Устанавливаем YOLO (Ultralytics)
RUN pip install --no-cache-dir ultralytics

# Отключаем GUI для OpenCV (чтобы не было проблем с Qt)
ENV OPENCV_VIDEOIO_PRIORITY_MSMF=0

# Экспонируем порт FastAPI
EXPOSE 8000

# Если папки app нет, создаём пустую для теста
RUN mkdir -p /app/app

# Команда запуска Uvicorn (FastAPI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
