#!/usr/bin/env python3
import os
import sys
import time
import hashlib
import requests
from pathlib import Path


def load_credentials():
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')

    if not all([cloud_name, api_key, api_secret]):
        print("Error: Missing Cloudinary credentials", file=sys.stderr)
        print("Set these environment variables:", file=sys.stderr)
        print("  CLOUDINARY_CLOUD_NAME", file=sys.stderr)
        print("  CLOUDINARY_API_KEY", file=sys.stderr)
        print("  CLOUDINARY_API_SECRET", file=sys.stderr)
        sys.exit(1)

    return cloud_name, api_key, api_secret


def sign_upload(params, api_secret):
    # Cloudinary requires SHA1 signature of sorted params + secret
    sorted_params = sorted(params.items())
    to_sign = "&".join([f"{k}={v}" for k, v in sorted_params]) + api_secret
    return hashlib.sha1(to_sign.encode()).hexdigest()


def upload_file(file_path, folder="uploads", public_id=None):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return None

    cloud_name, api_key, api_secret = load_credentials()

    if not public_id:
        public_id = Path(file_path).stem

    timestamp = int(time.time())
    params = {
        "folder": folder,
        "public_id": public_id,
        "timestamp": timestamp
    }

    signature = sign_upload(params, api_secret)

    data = {
        **params,
        "api_key": api_key,
        "signature": signature
    }

    # Figure out if it's a video or image
    video_exts = ('.mov', '.mp4', '.avi', '.webm', '.mkv', '.flv')
    resource_type = 'video' if file_path.lower().endswith(video_exts) else 'image'

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/{resource_type}/upload"

    try:
        with open(file_path, 'rb') as f:
            response = requests.post(url, data=data, files={'file': f})

        if response.status_code == 200:
            return response.json().get('secure_url')
        else:
            print(f"Upload failed: {response.status_code}", file=sys.stderr)
            print(response.text, file=sys.stderr)
            return None

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload.py <file_path> [folder] [public_id]")
        print("\nExamples:")
        print("  python upload.py photo.jpg")
        print("  python upload.py photo.jpg my-folder")
        print("  python upload.py photo.jpg my-folder custom-name")
        sys.exit(1)

    file_path = sys.argv[1]
    folder = sys.argv[2] if len(sys.argv) > 2 else "uploads"
    public_id = sys.argv[3] if len(sys.argv) > 3 else None

    url = upload_file(file_path, folder, public_id)

    if url:
        print(url)
    else:
        sys.exit(1)
