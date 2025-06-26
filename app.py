import cgi
import json
import logging
import math
import os
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

from PIL import Image

from db_manager import PostgresManager, postgres_config
from make_images_table import DOWNLOAD_PAGE_HEADER, create_pagination, get_hr_value

# Configuration
HOST, PORT = ('0.0.0.0', 5000)


# Detect if running in Docker
def is_docker():
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            return 'docker' in f.read() or 'kubepod' in f.read()
    except FileNotFoundError:
        return False


# Set paths based on environment
slash = '/' if is_docker() else ''  # '/' - Absolute path for Docker, '' - Relative path for non-Docker
UPLOAD_FOLDER = f'{slash}images'
LOG_FILE = f'{slash}logs/app.log'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Setup logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    encoding='utf-8',
)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def secure_filename(filename):
    return filename.replace('..', '').replace('/', '').replace('\\', '')


class ImageServer(BaseHTTPRequestHandler):
    db: Optional[PostgresManager] = None

    def do_GET(self):
        filepath = self.path[1:]
        if self.path == '/':
            self.serve_file('static/main.html', 'text/html')
            logging.info('Переход на главную страницу')
        elif self.path.startswith('/images-list'):
            page_number = self._get_page_number()
            self.serve_images_list(page_number=page_number)
            logging.info('Переход на страницу сохраненных изображений')
        elif self.path.startswith('/static/'):
            if os.path.exists(filepath):
                ext = os.path.splitext(filepath)[1]
                content_type = {
                    '.css': 'text/css',
                    '.js': 'application/javascript',
                    '.png': 'images-list/png',
                    '.jpg': 'images-list/jpeg',
                    '.jpeg': 'images-list/jpeg',
                    '.gif': 'images-list/gif',
                    '.html': 'text/html'
                }.get(ext, 'application/octet-stream')
                self.serve_file(filepath, content_type)
                if self.path == '/static/upload.html':
                    logging.info('Переход на страницу загрузки')
        else:
            self.send_error(404, 'Not Found')

    def _get_page_number(self) -> int:
        page_number = 1 if self.path == '/images-list' else int(self.path[18:])
        all_records = self.db.show_table()
        if not all_records:
            return 1
        if len(all_records) <= page_number * 10 - 10:
            page_number -= 1
        return page_number

    def do_POST(self):
        if self.path == '/upload':
            try:
                # Parse multipart form data
                content_type = self.headers.get('content-type')
                if not content_type or 'multipart/form-data' not in content_type:
                    self.send_error_response(400, 'Invalid content type')
                    logging.error('Invalid content type')
                    return

                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )

                if 'file' not in form:
                    self.send_error_response(400, 'No file part')
                    logging.error('No file part in request')
                    return

                file_item = form['file']
                if not file_item.filename:
                    self.send_error_response(400, 'No selected file')
                    logging.error('No selected file')
                    return

                if not allowed_file(file_item.filename):
                    self.send_error_response(400, 'Unsupported file format')
                    logging.error(f'Unsupported file format: {file_item.filename}')
                    return

                # Check file size
                file_data = file_item.file.read()
                if len(file_data) > MAX_FILE_SIZE:
                    self.send_error_response(400, 'File too large')
                    logging.error(f'File too large: {len(file_data)} bytes')
                    return

                # Generate unique filename
                original_name = file_item.filename
                file_type = original_name.rsplit('.', 1)[1].lower()
                filename = f'{uuid.uuid4().hex[:15]}.{file_type}'
                size = round(len(file_data) / 1000, 1)
                self.db.add_file(filename, original_name, size, file_type)

                filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))

                # Save file
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(file_data)
                    os.chmod(filepath, 0o664)  # Ensure readable by Nginx

                # Verify image
                try:
                    Image.open(filepath).verify()
                except Exception:
                    os.remove(filepath)
                    self.send_error_response(400, 'Invalid image file')
                    logging.error(f'Invalid image file: {filename}')
                    return

                # Send success response
                logging.info(f'Изображение {filename} загружено')
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'message': 'File uploaded successfully',
                    'filename': filename,
                    'url': f"/images-list/{filename}",
                    'host': self.headers.get('X-Forwarded-Host', self.headers['Host']),
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))

            except Exception as e:
                self.send_error_response(500, f'Error saving file: {str(e)}')
                logging.error(f'Error saving file: {str(e)}')

        else:
            self.send_error(404, 'Not Found')

    def do_DELETE(self):
        if self.path.startswith('/delete_image'):
            filename = self.path.split('/')[-1]
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if os.path.exists(filepath):
                    id_image = self.db.get_id_by_filename(filename)
                    self.db.delete_by_id(id_image=id_image)
                    os.remove(filepath)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True}).encode())
                    logging.info(f'Изображение {filename} удалено')
                    self.serve_images_list(page_number=1)
                else:
                    self.send_error(404, 'File Not Found')
            except Exception as e:
                self.send_error(500, f'Server Error: {str(e)}')
        else:
            self.send_error(404, 'Not Found')

    def serve_file(self, filepath, content_type):
        try:
            with open(filepath, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404, 'Not Found')

    def serve_images_list(self, page_number: int):
        try:
            image_list = self.db.get_page_by_page_num(page_number=page_number)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            html = DOWNLOAD_PAGE_HEADER
            if not image_list:
                html += '<p style="color: red; font-weight: bold;">НЕТ ЗАГРУЖЕННЫХ ИЗОБРАЖЕНИЙ</p>'
                logging.info('Отсутствуют загруженные изображения')
            else:
                pages_count = self.db.show_table()
                pages_count = math.ceil(len(pages_count) / 10)
                html += ('<table class="custom-table" id="resizableTable"><thead>'
                         '<tr><th>Name</th><th>Original Name</th><th>Size, kB</th><th>Uploaded at</th><th>Type</th>'
                         '<th>Delete</th></tr></thead><tbody>')
                for image in image_list:
                    html += get_hr_value(image)
                html += '</tbody></table>'
                if pages_count > 1:
                    html += create_pagination(page_number=page_number, pages_count=pages_count)

            html += '</body></html>'
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            self.send_error_response(500, f'Error listing images: {str(e)}')
            logging.error(f'Error listing images: {str(e)}')

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))


def run(db_object):
    ImageServer.db = db_object
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, ImageServer)
    logging.info('Starting server...')
    httpd.serve_forever()


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    with PostgresManager(postgres_config) as pm:
        pm.create_table()
        run(pm)
