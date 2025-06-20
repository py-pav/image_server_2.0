import cgi
import json
import logging
import os
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer

from PIL import Image
from make_images_table import DOWNLOAD_PAGE_HEADER, get_hr_value

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
    def do_GET(self):
        filepath = self.path[1:]
        if self.path == '/':
            self.serve_file('static/main.html', 'text/html')
            logging.info('Переход на главную страницу')
        elif self.path == '/images':
            self.serve_images_list()
            logging.info('Переход на страницу сохраненных изображений')
        elif self.path.startswith('/static/'):
            if os.path.exists(filepath):
                ext = os.path.splitext(filepath)[1]
                content_type = {
                    '.css': 'text/css',
                    '.js': 'application/javascript',
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.html': 'text/html'
                }.get(ext, 'application/octet-stream')
                self.serve_file(filepath, content_type)
                if self.path == '/static/upload.html':
                    logging.info('Переход на страницу загрузки')
        else:
            self.send_error(404, 'Not Found')

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
                filename = file_item.filename
                ext = filename.rsplit('.', 1)[1].lower()
                filename = filename.replace(f'.{ext}', '').lower()
                unique_filename = f'{uuid.uuid4().hex[:15]}_{filename}.{ext}'
                filename = secure_filename(unique_filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)

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
                    'url': f"/images/{filename}",
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
                    os.remove(filepath)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True}).encode())
                    logging.info(f'Изображение {filename} удалено')
                    self.serve_images_list()
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

    def serve_images_list(self):
        try:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
            html = DOWNLOAD_PAGE_HEADER
            if not files:
                html += '<p style="color: red; font-weight: bold;">FILES ARE MISSING</p>'
                logging.info('Отсутствуют загруженные изображения')
            else:
                html += ('<table class="custom-table" id="resizableTable"><thead>'
                         '<tr><th>Name</th><th>Url</th><th>Delete</th></tr></thead><tbody>')
                for file in files:
                    html += get_hr_value(file)
                html += '</tbody></table>'
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


def run():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, ImageServer)
    logging.info('Starting server...')
    httpd.serve_forever()


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    run()
