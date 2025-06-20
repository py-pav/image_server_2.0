// Копирование ссылки в буфер обмена по кнопке COPY
function copyToClipboard() {
    const linkInput = document.getElementById('image-link');
    linkInput.select();
    document.execCommand('copy');
    linkInput.blur();
}

// Загрузка картинки
function handleSubmit(event, files) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const form = document.querySelector('form');
    const errorDiv = document.getElementById('error-text');
    const linkInput = document.getElementById('image-link');
    const fileInput = document.getElementById('file-input');

    const formData = new FormData(form);

    // Если переданы файлы из drag and drop
    if (files && files.length > 0) {
        formData.set('file', files[0]);
    }
    // Иначе используем файлы из input
    else if (fileInput.files.length > 0) {
        formData.set('file', fileInput.files[0]);
    }
    // Если файлов нет вообще
    else {
        errorDiv.innerHTML = '<p style="color: red; font-weight: bold;">No file selected</p>';
        return;
    }

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            errorDiv.innerHTML = '<p style="color: red; font-weight: bold;">Upload failed: ' + data.error + '</p>';
            linkInput.value = '';
        } else {
            errorDiv.innerHTML = '<p style="color: green; font-weight: bold;">Successful download: ' + data.filename + '</p>';
            linkInput.value = data.host + data.url;
        }
    })
    .catch(error => {
        errorDiv.innerHTML = '<p style="color: red;">Error: ' + error + '</p>';
    });
}

// Обработчики для drag and drop
function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    event.dataTransfer.dropEffect = 'copy';
    document.getElementById('drop-area').style.backgroundColor = '#f0f0f0';
}

function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    document.getElementById('drop-area').style.backgroundColor = '';
}

function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    document.getElementById('drop-area').style.backgroundColor = '';

    const files = event.dataTransfer.files;

    if (files.length > 0) {
        // Обновляем файловый input
        const fileInput = document.getElementById('file-input');
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(files[0]);
        fileInput.files = dataTransfer.files;

        // Запускаем загрузку
        handleSubmit(event, files);
    }
}

// Инициализация событий после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-input');
    const dropArea = document.getElementById('drop-area');
    const form = document.querySelector('form');

    // Обработчик изменения файлового ввода
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleSubmit(null, null);
        }
    });

    // Обработчики drag and drop
    dropArea.addEventListener('dragover', handleDragOver);
    dropArea.addEventListener('dragleave', handleDragLeave);
    dropArea.addEventListener('drop', handleDrop);

    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        handleSubmit(e, null);
    });

    // Обработчик кнопки копирования
    const copyButton = document.querySelector('.inner-button');
    copyButton.addEventListener('click', copyToClipboard);
});