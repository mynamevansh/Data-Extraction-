# Receipt OCR Frontend

Modern React + Vite frontend for the receipt OCR backend.

## Setup

1. Install dependencies:

```bash
npm install
```

2. Create a local env file:

```bash
copy .env.example .env
```

3. Start the app:

```bash
npm run dev
```

## Configuration

- `VITE_API_BASE_URL`: backend base URL, for example `http://localhost:8000`
- `VITE_API_UPLOAD_PATH`: upload endpoint path, for example `/extract`

The frontend sends the selected image as multipart form data and expects the backend to return receipt JSON.
