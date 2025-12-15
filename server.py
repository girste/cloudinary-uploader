#!/usr/bin/env python3
import os
import sys
import json
import tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from upload import upload_file, load_credentials


class UploadHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != '/upload':
            self.send_error(404)
            return

        try:
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                self.json_response(400, {'error': 'Invalid content type'})
                return

            boundary = content_type.split('boundary=')[1].encode()
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            file_data, filename = self.extract_file(body, boundary)

            if not file_data or not filename:
                self.json_response(400, {'error': 'No file uploaded'})
                return

            # Save to temp, upload, then delete
            ext = os.path.splitext(filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(file_data)
                tmp_path = tmp.name

            try:
                url = upload_file(tmp_path)
                if url:
                    self.json_response(200, {'url': url})
                else:
                    self.json_response(500, {'error': 'Upload failed'})
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            self.json_response(500, {'error': str(e)})

    def extract_file(self, body, boundary):
        # Simple multipart parser - find the file part
        parts = body.split(b'--' + boundary)

        for part in parts:
            if b'filename=' not in part:
                continue

            # Get filename from Content-Disposition header
            lines = part.split(b'\r\n')
            filename = None
            for line in lines:
                if b'filename=' in line:
                    filename = line.split(b'filename=')[1].strip(b'"').decode()
                    break

            # File data is after the blank line
            data_start = part.find(b'\r\n\r\n') + 4
            data_end = part.rfind(b'\r\n')
            file_data = part[data_start:data_end]

            return file_data, filename

        return None, None

    def json_response(self, code, data):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")


if __name__ == "__main__":
    # Make sure we have credentials before starting
    try:
        load_credentials()
    except SystemExit:
        print("\nSet your Cloudinary credentials first:")
        print("  export CLOUDINARY_CLOUD_NAME='your_cloud_name'")
        print("  export CLOUDINARY_API_KEY='your_api_key'")
        print("  export CLOUDINARY_API_SECRET='your_api_secret'")
        print()
        sys.exit(1)

    port = int(os.getenv('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), UploadHandler)

    print(f"\nServer running at http://localhost:{port}")
    print("Ctrl+C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
        server.shutdown()
