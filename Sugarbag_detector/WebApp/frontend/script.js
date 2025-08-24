let currentFileId = '';
let currentFilename = '';

function setStatus(text, type = '') {
    const status = document.getElementById('status');
    status.textContent = text;
    status.className = type ? `status-${type}` : '';
}

async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const downloadBtn = document.getElementById('downloadBtn');

    if (!fileInput.files[0]) {
        setStatus('❌ Сначала выберите файл!', 'error');
        return;
    }

    const file = fileInput.files[0];
    uploadBtn.disabled = true;
    setStatus('⏳ Обработка файла...', 'processing');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://127.0.0.1:8000/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            currentFileId = result.file_id;
            currentFilename = result.filename;

            setStatus('✅ Файл успешно обработан!', 'success');
            downloadBtn.style.display = 'block';

        } else {
            setStatus('❌ Ошибка при загрузке файла', 'error');
        }

    } catch (error) {
        setStatus('❌ Ошибка подключения к серверу', 'error');
        console.error('Error:', error);
    } finally {
        uploadBtn.disabled = false;
    }
}

function downloadFile() {
    if (!currentFileId) {
        setStatus('❌ Нет файла для скачивания', 'error');
        return;
    }

    setStatus('⬇️ Начинаем скачивание...', 'processing');

    // Открываем ссылку для скачивания в новом окне
    const downloadUrl = `http://127.0.0.1:8000/download/${currentFileId}`;
    window.open(downloadUrl, '_blank');

    // Через секунду возвращаем обычный статус
    setTimeout(() => {
        setStatus('✅ Файл готов к скачиванию', 'success');
    }, 1000);
}

async function checkConnection() {
    try {
        const response = await fetch('http://127.0.0.1:8000/');
        if (response.ok) {
            console.log('✅ Сервер работает');
        }
    } catch (error) {
        setStatus('❌ Сервер не отвечает. Запустите бэкенд!', 'error');
        console.log('❌ Сервер не отведает');
    }
}

// Инициализация при загрузке страницы
function init() {
    // Назначение обработчиков событий
    document.getElementById('uploadBtn').addEventListener('click', uploadFile);
    document.getElementById('downloadBtn').addEventListener('click', downloadFile);

    // Показываем имя выбранного файла
    document.getElementById('fileInput').addEventListener('change', function(e) {
        if (e.target.files[0]) {
            setStatus(`📁 Выбран файл: ${e.target.files[0].name}`);
        }
    });

    // Проверим при загрузке страницы
    checkConnection();
}

// Запуск инициализации после загрузки DOM
document.addEventListener('DOMContentLoaded', init);