from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import uuid

app = FastAPI()

# Разрешаем все CORS запросы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем папки
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)

# Храним информацию о файлах
file_db = {}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Сохраняет файл и возвращает ID для скачивания"""

    # Создаем уникальный ID
    file_id = str(uuid.uuid4())

    # Сохраняем оригинальный файл
    original_path = f"uploads/{file_id}_{file.filename}"
    with open(original_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Создаем обработанный файл (просто копируем)
    processed_path = f"processed/{file_id}_processed_{file.filename}"
    from Sugar_detector import process_video
    process_video(original_path, processed_path)

    # Сохраняем информацию о файле
    file_db[file_id] = {
        "original_name": file.filename,
        "processed_path": processed_path
    }

    return {
        "file_id": file_id,
        "filename": file.filename,
        "message": "Файл обработан"
    }


@app.get("/download/{file_id}")
async def download_file(file_id: str):
    """Отдает обработанный файл по ID"""
    if file_id not in file_db:
        return {"error": "Файл не найден"}

    file_info = file_db[file_id]
    file_path = file_info["processed_path"]
    original_name = file_info["original_name"]

    if not os.path.exists(file_path):
        return {"error": "Файл был удален"}

    return FileResponse(
        path=file_path,
        filename=f"processed_{original_name}",
        media_type="video/mp4"
    )


@app.get("/")
async def root():
    return {"message": "Server is running!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)