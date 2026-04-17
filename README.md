# Sarvam AI — TTS, STT & Translate FastAPI Backend

End-to-end guide to set up a **Speech-to-Text (STT)**, **Text-to-Speech (TTS)**, and **Text Translation** agent using the official Sarvam AI Python SDK, powered by **FastAPI**, ready to integrate with your **Next.js** frontend.

---

## Architecture Overview

```
Next.js Frontend
      │
      │  HTTP / WebSocket
      ▼
FastAPI Backend  (this project)
      │
      │  REST / WebSocket
      ▼
Sarvam AI APIs
  ├── STT: Saaras v3 model   (transcribe, translate, codemix, translit)
  ├── TTS: Bulbul v3 model   (30+ voices, 11 languages)
  └── Translate: Sarvam text API
```

---

## 1. Prerequisites

| Tool | Version |
|------|---------|
| Python | ≥ 3.10 |
| pip | latest |
| Node.js | ≥ 18 (for Next.js) |
| Sarvam AI Account | [Sign up free](https://dashboard.sarvam.ai) |

---

## 2. Get Your Sarvam AI API Key

1. Go to [https://dashboard.sarvam.ai](https://dashboard.sarvam.ai) and create an account.
2. Navigate to **API Keys** in the sidebar.
3. Click **Generate Key** and copy it.
4. You'll use this as `SARVAM_API_KEY` in your `.env` file.

> Free tier includes credits to get started. Check [pricing](https://docs.sarvam.ai/api-reference-docs/getting-started/pricing) for limits.

---

## 3. Project Setup

### 3.1 Clone / create the project folder

```bash
mkdir sarvam-agent && cd sarvam-agent
```

### 3.2 Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3.3 Install dependencies

```bash
pip install -r requirements.txt
```

The project uses Sarvam's official Python SDK:

```bash
pip install -U sarvamai
```

### 3.4 Configure environment variables

```bash
cp .env.example .env
# Open .env and paste your Sarvam API key
```

`.env` should look like:
```
SARVAM_API_KEY=your_actual_key_here
```

---

## 4. Run the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit the interactive API docs at:
- **Test UI**: [http://localhost:8000/](http://localhost:8000/)
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Form Assistant

The home page now includes a profile-backed form assistant that reads dummy personal data from `data.json` and autofills matching inputs, selects, textareas, radio buttons, and checkboxes on the page.

It also includes an ITR-1 return form and a voice shortcut: say “fill ITR-1 form” and the agent will populate the return from `data.json`.

Additionally, 10 related tax forms are included and can be filled via voice commands as well:
ITR-2, ITR-3, ITR-4, Form 80C, Form 80D, Form 80E, Form 80G, HRA Claim, Form 16, and Form 26AS.
You can also say “fill all tax forms” to populate all related forms at once.

To customise it, edit `data.json` with your own personal details and reload the page.

---

## 5. API Endpoints

### 5.1 Health Check
```
GET /health
```
Returns `{ "status": "ok", "sarvam_key_set": true, "sarvam_sdk": "sarvamai" }`.

---

### 5.2 STT — REST (File Upload)

```
POST /stt/transcribe
Content-Type: multipart/form-data
```

**Form fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `file` | file | required | Audio file (WAV, MP3, WebM, etc.) |
| `language_code` | string | auto-detect | BCP-47 code e.g. `hi-IN`, `kn-IN`, `en-IN`; use `unknown` for streaming auto-detect |
| `model` | string | `saaras:v3` | `saaras:v3` (recommended) or `saarika:v2.5` |
| `mode` | string | `transcribe` | `transcribe`, `translate`, `verbatim`, `translit`, `codemix` |
| `input_audio_codec` | string | auto-detect | Required only for raw PCM formats such as `pcm_s16le`, `pcm_l16`, `pcm_raw` |

**Response:**
```json
{
  "request_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ef",
  "transcript": "नमस्ते, आप कैसे हैं?",
  "language_code": "hi-IN",
  "language_probability": 0.95,
  "timestamps": null,
  "diarized_transcript": null
}
```

**cURL example:**
```bash
curl -X POST http://localhost:8000/stt/transcribe \
  -F "file=@audio.wav" \
  -F "language_code=hi-IN" \
  -F "model=saaras:v3" \
  -F "mode=transcribe"
```

> **Note:** Max audio duration is 30 seconds for REST. For longer files, you would extend this to use Sarvam's [Batch API](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/batch-api).

---

### 5.3 STT — WebSocket (Real-time Streaming)

```
WS ws://localhost:8000/stt/stream
```

**Client protocol:**

```
Step 1 → Send config JSON:
  { "language_code": "unknown", "model": "saaras:v3", "mode": "transcribe" }

Step 2 → Send binary audio chunks (WAV or PCM 16kHz)
  <binary data> ...

Step 3 → Send end signal:
  { "type": "end" }
```

**Server events:**
```json
{ "type": "data", "data": { "transcript": "हाँ, मैं ठीक हूँ", "language_code": "hi-IN" } }
{ "error": "some error message" }
```

---

### 5.4 Text Translation

```
POST /text/translate
Content-Type: application/json
```

**Request body:**
```json
{
  "input": "Hi, My Name is Vinayak.",
  "source_language_code": "auto",
  "target_language_code": "gu-IN",
  "speaker_gender": "Male"
}
```

**Response:**
```json
{
  "request_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ef",
  "translated_text": "હાય, મારું નામ વિનાયક છે.",
  "source_language_code": "en-IN"
}
```

---

### 5.5 TTS — REST

```
POST /tts/generate
Content-Type: application/json
```

**Request body:**
```json
{
  "text": "नमस्ते, आप कैसे हैं?",
  "target_language_code": "hi-IN",
  "speaker": "shubh",
  "model": "bulbul:v3",
  "pace": 1.0,
  "output_format": "wav"
}
```

| Field | Options | Notes |
|-------|---------|-------|
| `target_language_code` | `hi-IN`, `kn-IN`, `ta-IN`, `te-IN`, `ml-IN`, `mr-IN`, `gu-IN`, `bn-IN`, `en-IN`, etc. | 11 languages for TTS |
| `speaker` | `shubh`, `aditya`, `ritu`, `priya`, `neha`, `rahul`, `pooja`, `rohan`, `simran`, `kavya` and more | Speaker names are lowercase and model-specific |
| `model` | `bulbul:v3` (recommended), `bulbul:v2` | v3 has better quality |
| `pace` | `0.5` – `2.0` | 1.0 = normal speed |
| `output_format` | `wav`, `mp3`, `opus`, `flac`, `aac` | |

**Response:** Binary audio stream (`audio/wav` or other format).

**cURL example:**
```bash
curl -X POST http://localhost:8000/tts/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "नमस्ते", "target_language_code": "hi-IN", "speaker": "shubh"}' \
  --output output.wav
```

---

### 5.6 TTS — WebSocket (Real-time Streaming)

```
WS ws://localhost:8000/tts/stream
```

**Client protocol:**

```
Step 1 → Send config JSON:
  {
    "speaker": "shubh",
    "target_language_code": "hi-IN",
    "model": "bulbul:v3"
  }

Step 2 → Send text chunks:
  { "text": "नमस्ते, आपका स्वागत है।" }

Step 3 → Flush buffer (optional, forces audio generation):
  { "type": "flush" }

Step 4 → End stream:
  { "type": "end" }
```

**Server response:**
- Binary audio chunks
- `{ "type": "event", "data": { "event_type": "final" } }` when complete

---

## 6. Supported Languages

| Language | Code |
|----------|------|
| Hindi | `hi-IN` |
| Kannada | `kn-IN` |
| Tamil | `ta-IN` |
| Telugu | `te-IN` |
| Malayalam | `ml-IN` |
| Marathi | `mr-IN` |
| Gujarati | `gu-IN` |
| Bengali | `bn-IN` |
| Punjabi | `pa-IN` |
| Odia | `od-IN` |
| English (India) | `en-IN` |

---

## 7. Integrating with Next.js Frontend

### 7.1 STT — File Upload (REST)

```typescript
// lib/stt.ts
export async function transcribeAudio(audioBlob: Blob, languageCode = "hi-IN") {
  const formData = new FormData();
  formData.append("file", audioBlob, "recording.wav");
  formData.append("language_code", languageCode);
  formData.append("model", "saaras:v3");
  formData.append("mode", "transcribe");

  const res = await fetch("http://localhost:8000/stt/transcribe", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json(); // { transcript, language_code }
}
```

### 7.2 STT — Real-time Streaming (WebSocket)

```typescript
// lib/sttStream.ts
export function createSTTStream(languageCode = "unknown") {
  const ws = new WebSocket("ws://localhost:8000/stt/stream");

  ws.onopen = () => {
    ws.send(JSON.stringify({ language_code: languageCode, model: "saaras:v3" }));
  };

  // After onopen, send binary PCM audio chunks:
  // ws.send(audioChunkArrayBuffer);

  // To stop:
  // ws.send(JSON.stringify({ type: "end" }));

  return ws;
}
```

### 7.3 TTS — Fetch and Play Audio (REST)

```typescript
// lib/tts.ts
export async function speak(text: string, languageCode = "hi-IN") {
  const res = await fetch("http://localhost:8000/tts/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      target_language_code: languageCode,
      speaker: "shubh",
      model: "bulbul:v3",
    }),
  });

  if (!res.ok) throw new Error(await res.text());

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  audio.play();
  // Cleanup: audio.onended = () => URL.revokeObjectURL(url);
}
```

### 7.4 TTS — Streaming (WebSocket)

```typescript
// lib/ttsStream.ts
export function createTTSStream(config = {}) {
  const ws = new WebSocket("ws://localhost:8000/tts/stream");
  const audioContext = new AudioContext();
  const chunks: ArrayBuffer[] = [];

  ws.onopen = () => {
    ws.send(JSON.stringify({
      speaker: "shubh",
      target_language_code: "hi-IN",
      model: "bulbul:v3",
      ...config,
    }));
  };

  ws.onmessage = async (event) => {
    if (event.data instanceof Blob) {
      const buf = await event.data.arrayBuffer();
      // Decode and play PCM audio chunk
      const decoded = await audioContext.decodeAudioData(buf);
      const source = audioContext.createBufferSource();
      source.buffer = decoded;
      source.connect(audioContext.destination);
      source.start();
    }
  };

  return {
    send: (text: string) => ws.send(JSON.stringify({ text })),
    flush: () => ws.send(JSON.stringify({ type: "flush" })),
    end: () => ws.send(JSON.stringify({ type: "end" })),
    close: () => ws.close(),
  };
}
```

### 7.5 Recording Microphone Audio (Next.js)

```typescript
// hooks/useAudioRecorder.ts
import { useRef, useState } from "react";

export function useAudioRecorder() {
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const [isRecording, setIsRecording] = useState(false);

  const start = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.current = new MediaRecorder(stream);
    chunks.current = [];

    mediaRecorder.current.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.current.push(e.data);
    };

    mediaRecorder.current.start(250); // collect in 250ms chunks
    setIsRecording(true);
  };

  const stop = (): Promise<Blob> =>
    new Promise((resolve) => {
      mediaRecorder.current!.onstop = () => {
        const blob = new Blob(chunks.current, { type: "audio/webm" });
        resolve(blob);
      };
      mediaRecorder.current!.stop();
      setIsRecording(false);
    });

  return { start, stop, isRecording };
}
```

---

## 8. CORS Configuration

For production, update the CORS origins in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-nextjs-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 9. Deployment Tips

- **Environment:** Set `SARVAM_API_KEY` as a secret in your hosting provider (Railway, Render, AWS, GCP, etc.)
- **Process manager:** Use `gunicorn` with `uvicorn` workers for production:
  ```bash
  gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
  ```
- **HTTPS/WSS:** Use a reverse proxy (nginx, Caddy) with TLS so browser WebSocket connections use `wss://`
- **Rate limits:** Sarvam enforces per-key rate limits. Add retry logic with exponential backoff for production.

---

## 10. Common Errors

| Code | Cause | Fix |
|------|-------|-----|
| 401 | Invalid API key | Check `SARVAM_API_KEY` in `.env` |
| 422 | Language not detected | Pass `language_code` explicitly |
| 429 | Rate limit exceeded | Add exponential backoff; upgrade plan |
| 500 | Server error | Retry; check Sarvam status page |

---

## 11. Useful Links

- [Sarvam Dashboard](https://dashboard.sarvam.ai) — API keys, playground, usage
- [STT Docs](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/overview)
- [TTS Docs](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/text-to-speech/overview)
- [Sarvam Discord](https://discord.com/invite/5rAsykttcs) — Community support
- [Sarvam API Status](https://status.sarvam.ai)
