# Cloudinary Uploader

Simple, minimal tool to upload images and videos to Cloudinary.

## Features

- CLI tool for quick uploads
- Minimal web interface with drag & drop
- Bulk upload support
- No database, no complexity

## Installation

```bash
pip install requests
```

## Setup

Set your Cloudinary credentials as environment variables:

```bash
export CLOUDINARY_CLOUD_NAME='your_cloud_name'
export CLOUDINARY_API_KEY='your_api_key'
export CLOUDINARY_API_SECRET='your_api_secret'
```

Or create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env with your credentials
```

## Usage

### CLI Upload

```bash
# Upload an image
python upload.py photo.jpg

# Upload to a specific folder
python upload.py photo.jpg my-folder

# Upload with custom name
python upload.py photo.jpg my-folder custom-name
```

Returns the Cloudinary URL:

```
https://res.cloudinary.com/your_cloud/image/upload/v1234567890/uploads/photo.jpg
```

### Web Interface

Start the server:

```bash
python server.py
```

Open http://localhost:8000 in your browser.

Drag and drop images or click to select files. Upload single or multiple files at once.

## How It Works

1. Takes your image/video file
2. Uploads it to Cloudinary via their API
3. Returns the public URL

That's it. No database, no storage, just a simple uploader.

## Notes

- Supports images (jpg, png, webp, etc.) and videos (mp4, mov, etc.)
- Files are uploaded to your Cloudinary account
- Get your credentials from https://cloudinary.com/console

## License

Public domain. Do whatever you want with it.
