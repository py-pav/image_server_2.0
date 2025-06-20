SCRIPT_FOR_DELETE = '''
<script>
function deleteImage(filename) {
    if (confirm('Вы уверены, что хотите удалить это изображение?')) {
        fetch(`/delete_image/${filename}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {                
                window.location.reload();
            } else {
                alert('Ошибка при удалении изображения');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при удалении');
        });
    }
}
</script>
'''

DOWNLOAD_PAGE_HEADER = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Uploaded Images</title>
    {SCRIPT_FOR_DELETE}
    <link rel="icon" href="/static/pictures/favicon.ico" type="image/x-icon">
    <link href="/static/styles.css" rel="stylesheet" type="text/css" />
</head>
<body class="upload-body">
    <header style="text-align: center;">
        <h1>Upload Photos</h1>
        <h2>Upload selfies, memes, or any fun pictures here.</h2>
    </header>
    <div class="navigation-links" style="margin-top: 50px; margin-bottom: 50px;">
        <a href="#link2" style="color: #ADC0F8; cursor: pointer;" onclick="window.location.href='/static/upload.html'">Upload</a>
        <a style="color: #0060FF;">Images</a>
    </div>    
'''


def get_hr_value(file_name: str) -> str:
    result = f'''
        <tr>
            <td>
                <div class="first-column-content">
                    <img src="static/pictures/vector.png" alt="vector">
                    <span>{file_name[file_name.find('_') + 1:]}</span>                                      
                </div>
            </td>
            <td>
                <div class="middle-column-content"><a href="/images/{file_name}" target="_blank">{file_name}</a></div>
            </td>
            <td>
                <div class="lust-column-content">
                    <img src="static/pictures/delete.png" alt="delete" class="clickable-image"
                         onclick="deleteImage('{file_name}')">
                </div>
            </td>
        </tr>    
    '''
    return result
