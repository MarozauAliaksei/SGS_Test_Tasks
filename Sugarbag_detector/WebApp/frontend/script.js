const backendUrl = 'http://localhost:8000'; // локально через браузер

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
        const response = await fetch(`${backendUrl}/upload`, {
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
            const errText = await response.text();
            setStatus(`❌ Ошибка при загрузке файла: ${errText}`, 'error');
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

    const downloadUrl = `${backendUrl}/download/${currentFileId}`;
    window.open(downloadUrl, '_blank');
    setStatus('✅ Файл готов к скачиванию', 'success');
}

async function checkConnection() {
    try {
        const response = await fetch(`${backendUrl}/`);
        if (!response.ok) setStatus('❌ Сервер вернул ошибку', 'error');
    } catch (error) {
        setStatus('❌ Сервер не отвечает. Запустите бэкенд!', 'error');
    }
}

function init() {
    document.getElementById('uploadBtn').addEventListener('click', uploadFile);
    document.getElementById('downloadBtn').addEventListener('click', downloadFile);

    document.getElementById('fileInput').addEventListener('change', e => {
        if (e.target.files[0]) {
            setStatus(`📁 Выбран файл: ${e.target.files[0].name}`);
        }
    });

    checkConnection();
}

document.addEventListener('DOMContentLoaded', init);
