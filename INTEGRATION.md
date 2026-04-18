# Integration Guide

This project is already split into two folders:

- `backend/` — FastAPI server, routes, and API logic
- `frontend/` — browser UI and static profile data

Use the steps below to integrate it into another project that uses the same `frontend/` + `backend/` structure.

## 1. Copy the folders

Copy these files and folders into the target project:

- `backend/`
- `frontend/`
- optional compatibility shim `main.py` in the project root, if you want to keep `uvicorn main:app`

If the target project already has its own `frontend/` or `backend/`, merge the contents carefully instead of overwriting them.

## 2. Keep the backend entrypoint

The FastAPI app lives in `backend/main.py` and should be started from that module:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

For production, use:

```bash
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

If the target project already starts the backend from a different module name, update its entrypoint to point at `backend.main:app` or create a small wrapper that imports `app` from there.

## 3. Keep the frontend files in place

The backend expects these exact paths:

- `frontend/ui.html`
- `frontend/data.json`

The root route `/` serves `frontend/ui.html`.
The `/data.json` route serves `frontend/data.json`.

If you move either file, update the paths in `backend/main.py`.

## 4. Required environment variables

Set these in the target project:

- `SARVAM_API_KEY`
- `OPENAI_API_KEY`

Example `.env` file:

```env
SARVAM_API_KEY=your_sarvam_key
OPENAI_API_KEY=your_openai_key
```

## 5. Install dependencies

Make sure the target project has the same Python dependencies installed.

If it uses `requirements.txt`:

```bash
pip install -r requirements.txt
```

If it uses `pyproject.toml`, install the package set used by the backend:

- FastAPI
- Uvicorn
- Pydantic
- python-dotenv
- python-multipart
- Sarvam SDK
- OpenAI SDK
- websockets
- httpx

## 6. Verify the integration

After copying the folders and setting environment variables:

1. Start the backend.
2. Open `http://localhost:8000/`.
3. Confirm the frontend loads.
4. Click **Load data.json** in the form assistant.
5. Test a voice command like:
   - `fill ITR-1 form`
   - `fill ITR-2`
   - `fill all tax forms`

## 7. If the target project already has its own frontend

If the other project already serves a different UI, you can still reuse the backend by:

- keeping `backend/main.py`
- copying only the routes and helper logic you need
- removing the `/` route if the other app serves HTML elsewhere
- keeping `/data.json` if the UI needs profile data

## 8. Common integration issues

### 404 for `/`
Check that `frontend/ui.html` exists and that `backend/main.py` points to `frontend/`.

### 404 for `/data.json`
Check that `frontend/data.json` exists and is valid JSON.

### Backend starts but voice features fail
Check these:

- `SARVAM_API_KEY` is set
- `OPENAI_API_KEY` is set
- microphone access is allowed in the browser
- the frontend is opened from the same backend origin

### UI loads but autofill does nothing
Confirm that the form field IDs, names, and labels in the target project still match the heuristics used by the form assistant.

## 9. Recommended target structure

```text
project-root/
├── backend/
│   ├── __init__.py
│   └── main.py
├── frontend/
│   ├── ui.html
│   └── data.json
├── .env
├── requirements.txt or pyproject.toml
└── main.py   (optional compatibility shim)
```

## 10. Minimal integration checklist

- Copy `backend/` and `frontend/`
- Set `SARVAM_API_KEY` and `OPENAI_API_KEY`
- Run `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`
- Confirm `http://localhost:8000/` works
- Test voice-triggered form filling
