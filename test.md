# Testing Guide

Use this guide to test every endpoint in the FastAPI backend.

## 1. Start The Server

From the project root:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal open. In a second terminal, run the tests below.

## 2. Check Environment

Confirm your API key is loaded:

```bash
echo "$SARVAM_API_KEY"
```

If it prints nothing, export it:

```bash
export SARVAM_API_KEY="YOUR_SARVAM_API_KEY"
```

If you use `.env`, confirm it contains:

```text
SARVAM_API_KEY=YOUR_SARVAM_API_KEY
```

## 3. Health Check

```bash
curl http://localhost:8000/health
```

Expected shape:

```json
{
  "status": "ok",
  "sarvam_key_set": true,
  "sarvam_sdk": "sarvamai"
}
```

If `sarvam_key_set` is `false`, fix `SARVAM_API_KEY` before testing Sarvam calls.

## 4. API Docs

Open:

```text
http://localhost:8000/
```

Use the browser UI to test:

```text
Text To Speech
Speech To Text file upload
Speech To Text microphone recording
```

Open:

```text
http://localhost:8000/docs
```

You should see Swagger UI with these endpoints:

```text
GET  /health
POST /stt/transcribe
POST /tts/generate
POST /text/translate
WS   /stt/stream
WS   /tts/stream
```

The root route serves the browser test UI.

## 5. Text Translation

```bash
curl -X POST http://localhost:8000/text/translate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hi, My Name is Vinayak.",
    "source_language_code": "auto",
    "target_language_code": "gu-IN",
    "speaker_gender": "Male"
  }'
```

Expected shape:

```json
{
  "request_id": "...",
  "translated_text": "...",
  "source_language_code": "..."
}
```

Pass condition: `translated_text` is non-empty Gujarati text.

## 6. Text To Speech

Generate a WAV file:

```bash
curl -X POST http://localhost:8000/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_language_code": "hi-IN",
    "speaker": "shubh",
    "model": "bulbul:v3",
    "pace": 1.0,
    "output_format": "wav"
  }' \
  --output output.wav
```

Check that the file exists and is not empty:

```bash
ls -lh output.wav
file output.wav
```

Optional playback:

```bash
ffplay output.wav
```

If `ffplay` is not installed, use any audio player.

Pass condition: `output.wav` is created and plays speech.

## 7. Speech To Text

You need a short audio file, ideally under 30 seconds.

If you already have one:

```bash
curl -X POST http://localhost:8000/stt/transcribe \
  -F "file=@audio.wav" \
  -F "model=saaras:v3" \
  -F "mode=transcribe"
```

Expected shape:

```json
{
  "request_id": "...",
  "transcript": "...",
  "language_code": "...",
  "language_probability": 0.95,
  "timestamps": null,
  "diarized_transcript": null
}
```

Pass condition: `transcript` is non-empty and matches the audio.

### Test STT With TTS Output

You can also reuse the TTS output from step 6:

```bash
curl -X POST http://localhost:8000/stt/transcribe \
  -F "file=@output.wav" \
  -F "model=saaras:v3" \
  -F "mode=transcribe"
```

Pass condition: the transcript reflects the generated speech.

### Test Saaras v3 Modes

Run these one by one:

```bash
curl -X POST http://localhost:8000/stt/transcribe \
  -F "file=@audio.wav" \
  -F "model=saaras:v3" \
  -F "mode=translate"
```

```bash
curl -X POST http://localhost:8000/stt/transcribe \
  -F "file=@audio.wav" \
  -F "model=saaras:v3" \
  -F "mode=verbatim"
```

```bash
curl -X POST http://localhost:8000/stt/transcribe \
  -F "file=@audio.wav" \
  -F "model=saaras:v3" \
  -F "mode=translit"
```

```bash
curl -X POST http://localhost:8000/stt/transcribe \
  -F "file=@audio.wav" \
  -F "model=saaras:v3" \
  -F "mode=codemix"
```

Pass condition: each request returns a valid JSON response with a non-empty `transcript`.

## 8. TTS WebSocket Streaming

Create a temporary test client:

```bash
cat > /tmp/test_tts_ws.py <<'PY'
import asyncio
import json
import websockets

async def main():
    uri = "ws://localhost:8000/tts/stream"
    with open("tts_stream_output.mp3", "wb") as output:
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({
                "speaker": "shubh",
                "target_language_code": "hi-IN",
                "model": "bulbul:v3",
                "output_format": "mp3"
            }))
            await ws.send(json.dumps({"text": "Hello, this is a streaming text to speech test."}))
            await ws.send(json.dumps({"type": "end"}))

            async for message in ws:
                if isinstance(message, bytes):
                    output.write(message)
                    print(f"audio chunk: {len(message)} bytes")
                else:
                    print("event:", message)
                    data = json.loads(message)
                    if data.get("type") == "event" and data.get("data", {}).get("event_type") == "final":
                        break

asyncio.run(main())
PY

python /tmp/test_tts_ws.py
```

Check output:

```bash
ls -lh tts_stream_output.mp3
file tts_stream_output.mp3
```

Pass condition: `tts_stream_output.mp3` exists, is not empty, and plays speech.

## 9. STT WebSocket Streaming

This test sends a WAV file as one binary message. For real-time apps, send smaller chunks from the microphone.

Create a temporary test client:

```bash
cat > /tmp/test_stt_ws.py <<'PY'
import asyncio
import json
import sys
import websockets

AUDIO_FILE = sys.argv[1] if len(sys.argv) > 1 else "output.wav"

async def main():
    uri = "ws://localhost:8000/stt/stream"
    async with websockets.connect(uri, max_size=10_000_000) as ws:
        await ws.send(json.dumps({
            "language_code": "unknown",
            "model": "saaras:v3",
            "mode": "transcribe",
            "encoding": "audio/wav",
            "sample_rate": 16000
        }))

        with open(AUDIO_FILE, "rb") as audio:
            await ws.send(audio.read())

        await ws.send(json.dumps({"type": "end"}))

        async for message in ws:
            print(message)
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue
            if data.get("type") in {"data", "error"}:
                break

asyncio.run(main())
PY

python /tmp/test_stt_ws.py output.wav
```

Pass condition: the script prints a transcript event or a clear API error. If the transcript is poor, test with a cleaner 16 kHz WAV file.

## 10. Common Failures

### 500 with `SARVAM_API_KEY not configured`

Set the key:

```bash
export SARVAM_API_KEY="YOUR_SARVAM_API_KEY"
```

Then restart `uvicorn`.

### 401 from Sarvam

The key is missing, invalid, expired, or copied incorrectly.

### 422 from Sarvam

Usually a bad language code, mode, model, audio codec, or malformed audio file.

### Empty or Bad STT Transcript

Try:

```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 audio.wav
```

Then rerun the STT tests with `audio.wav`.

## 11. Full Smoke Test Order

Run in this order:

```text
1. GET /health
2. POST /text/translate
3. POST /tts/generate
4. POST /stt/transcribe using output.wav
5. WS /tts/stream
6. WS /stt/stream using output.wav
```

If all six pass, the backend is working end to end.
