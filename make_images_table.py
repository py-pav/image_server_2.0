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


def get_hr_value(image: tuple) -> str:
    _, file_name, original_name, size, uploaded_date, file_type = image
    result = f'''
        <tr>
            <td>
                <div class="first-column-content">
                    <img src="static/pictures/vector.png" alt="vector">
                    <a href="/images/{file_name}" target="_blank">{file_name}</a>                                     
                </div>
            </td>
            <td><div class="middle-column-content">{original_name}</div></td>
            <td><div class="middle-column-content">{size}</div></td>
            <td><div class="middle-column-content">{uploaded_date.strftime("%Y-%m-%d %H:%M:%S")}</div></td>
            <td><div class="middle-column-content">{file_type}</div></td>
            <td>
                <div class="lust-column-content">
                    <img src="static/pictures/delete.png" alt="delete" class="clickable-image"
                    onclick="deleteImage('{file_name}')">
                </div>
            </td>
        </tr>    
    '''
    return result


def create_pagination(page_number: int, pages_count: int) -> str:
    active_btn = 'style="color: #0060FF; cursor: pointer;" onclick="window.location.href='
    not_active_btn = '<a style="color: #ADC0F8;">'
    page_link = '/images-list?page='
    next_link, previous_link = f'{page_link}{page_number + 1}', f'{page_link}{page_number - 1}'

    if page_number == 1:
        previous_page = f'{not_active_btn}'
        next_page = f'''<a href="{next_link}" {active_btn}='{next_link}'">'''
    elif page_number == pages_count:
        previous_page = f'''<a href="{previous_link}" {active_btn}='{previous_link}'">'''
        next_page = f'{not_active_btn}'
    else:
        previous_page = f'''<a href="{previous_link}" {active_btn}='{previous_link}'">'''
        next_page = f'''<a href="{next_link}" {active_btn}='{next_link}'">'''
    result = f'''
        <div class="navigation-links" style="margin-top: 50px; margin-bottom: 50px;">
            {previous_page}Previous Page</a>                      
            <div>{page_number}</div>
            <div>(total {pages_count})</div>
            {next_page}Next Page</a>  
        </div>
    '''
    return result
