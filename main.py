"""
Sarvam AI TTS & STT FastAPI Backend
====================================
Endpoints:
  POST /stt/transcribe       - Upload audio file → get transcript
  POST /stt/stream           - WebSocket proxy for real-time STT
  POST /tts/generate         - Text → audio file (WAV/MP3)
  WS   /tts/stream           - WebSocket streaming TTS
  GET  /health               - Health check
"""

import os
import io
import json
import base64
import asyncio
import contextlib
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Optional
from dotenv import load_dotenv
from sarvamai import AsyncSarvamAI
from sarvamai.core.api_error import ApiError

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
APP_DIR = Path(__file__).resolve().parent
_sarvam_client: Optional[AsyncSarvamAI] = None
_sarvam_client_key: Optional[str] = None

app = FastAPI(
    title="Sarvam AI TTS & STT Agent",
    description="FastAPI backend for Sarvam AI Speech-to-Text, Text-to-Speech, and Translate using the official SDK",
    version="1.1.0",
)

# Allow all origins during development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Pydantic Models ────────────────────────────────────────────────────────

class TTSRequest(BaseModel):
    text: str
    target_language_code: str = "hi-IN"    # BCP-47 language tag
    speaker: str = "shubh"                  # bulbul:v3 default voice
    model: str = "bulbul:v3"               # bulbul:v2 or bulbul:v3
    pace: float = 1.0                       # 0.5 – 2.0
    output_format: str = "wav"              # wav | mp3 | opus etc.
    speech_sample_rate: Optional[int] = None
    temperature: Optional[float] = None


class TranslateRequest(BaseModel):
    input: str
    source_language_code: str = "auto"
    target_language_code: str = "gu-IN"
    speaker_gender: Optional[str] = "Male"
    mode: Optional[str] = None
    model: Optional[str] = None
    output_script: Optional[str] = None
    numerals_format: Optional[str] = None


class STTResponse(BaseModel):
    request_id: Optional[str] = None
    transcript: str
    language_code: Optional[str] = None
    language_probability: Optional[float] = None
    timestamps: Optional[dict[str, Any]] = None
    diarized_transcript: Optional[dict[str, Any]] = None


class TranslateResponse(BaseModel):
    request_id: Optional[str] = None
    translated_text: str
    source_language_code: Optional[str] = None


# ─── Helpers ────────────────────────────────────────────────────────────────

def _get_sarvam_api_key() -> str:
    api_key = os.getenv("SARVAM_API_KEY") or SARVAM_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="SARVAM_API_KEY not configured")
    return api_key


def _sarvam() -> AsyncSarvamAI:
    global _sarvam_client, _sarvam_client_key

    api_key = _get_sarvam_api_key()
    if _sarvam_client is None or _sarvam_client_key != api_key:
        _sarvam_client = AsyncSarvamAI(api_subscription_key=api_key)
        _sarvam_client_key = api_key
    return _sarvam_client


def _sdk_model_dump(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    return value


def _clean_audio_content_type(content_type: Optional[str]) -> str:
    if not content_type:
        return "audio/wav"
    return content_type.split(";", 1)[0].strip().lower()


def _raise_sdk_error(exc: ApiError) -> None:
    status_code = exc.status_code or 502
    detail = exc.body if exc.body is not None else str(exc)
    raise HTTPException(status_code=status_code, detail=detail)


# ─── Health ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def ui():
    return (APP_DIR / "ui.html").read_text(encoding="utf-8")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "sarvam_key_set": bool(os.getenv("SARVAM_API_KEY") or SARVAM_API_KEY),
        "sarvam_sdk": "sarvamai",
    }


# ─── STT REST ───────────────────────────────────────────────────────────────

@app.post("/stt/transcribe", response_model=STTResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language_code: Optional[str] = Form(None),   # e.g. "hi-IN"; omit or use "unknown" for auto-detect
    model: str = Form("saaras:v3"),              # saaras:v3 (recommended) | saarika:v2.5
    mode: str = Form("transcribe"),              # transcribe | translate | verbatim | translit | codemix
    input_audio_codec: Optional[str] = Form(None),
):
    """
    Upload an audio file and receive a text transcript.
    Supported formats: WAV, MP3, AAC, AIFF, OGG, OPUS, FLAC, MP4/M4A, WebM, AMR, WMA, PCM.
    Max duration: 30 seconds (use /stt/batch for longer files).
    """
    audio_bytes = await file.read()

    kwargs: dict[str, Any] = {
        "model": model,
        "mode": mode,
        "file": (file.filename, io.BytesIO(audio_bytes), _clean_audio_content_type(file.content_type)),
    }
    if language_code:
        kwargs["language_code"] = language_code
    if input_audio_codec:
        kwargs["input_audio_codec"] = input_audio_codec

    try:
        response = await _sarvam().speech_to_text.transcribe(**kwargs)
    except ApiError as exc:
        _raise_sdk_error(exc)

    return STTResponse(
        request_id=response.request_id,
        transcript=response.transcript,
        language_code=response.language_code,
        language_probability=response.language_probability,
        timestamps=_sdk_model_dump(response.timestamps) if response.timestamps else None,
        diarized_transcript=_sdk_model_dump(response.diarized_transcript) if response.diarized_transcript else None,
    )


# ─── STT WebSocket (Real-time Streaming) ────────────────────────────────────

@app.websocket("/stt/stream")
async def stt_stream(websocket: WebSocket):
    """
    Real-time STT via WebSocket.

    Protocol (client → server):
      1. Send JSON config:   {"language_code": "unknown", "model": "saaras:v3"}
      2. Send binary audio chunks (WAV or raw PCM at 16 kHz)
      3. Send JSON end signal: {"type": "end"}

    Protocol (server → client):
      - JSON transcript events: {"transcript": "...", "is_final": true/false}
      - JSON error events:      {"error": "..."}
    """
    await websocket.accept()

    try:
        _get_sarvam_api_key()
    except HTTPException:
        await websocket.send_json({"error": "SARVAM_API_KEY not configured"})
        await websocket.close()
        return

    # Receive config from the client first
    try:
        config_msg = await websocket.receive_text()
        config = json.loads(config_msg)
    except Exception:
        await websocket.send_json({"error": "First message must be a JSON config"})
        await websocket.close()
        return

    language_code = config.get("language_code", "unknown")
    model = config.get("model", "saaras:v3")
    mode = config.get("mode", "transcribe")
    encoding = config.get("encoding", "audio/wav")
    sample_rate = int(config.get("sample_rate", 16000))

    connect_kwargs = {
        "language_code": language_code,
        "model": model,
        "mode": mode,
    }
    for option in ("high_vad_sensitivity", "vad_signals", "flush_signal", "input_audio_codec"):
        if config.get(option) is not None:
            connect_kwargs[option] = config[option]
    if config.get("connection_sample_rate") is not None:
        connect_kwargs["sample_rate"] = str(config["connection_sample_rate"])

    try:
        async with _sarvam().speech_to_text_streaming.connect(**connect_kwargs) as sarvam_ws:

            async def forward_audio():
                """Forward client audio chunks through the official Sarvam SDK."""
                try:
                    while True:
                        msg = await websocket.receive()
                        if msg.get("type") == "websocket.disconnect":
                            break
                        if msg.get("bytes") is not None:
                            audio_b64 = base64.b64encode(msg["bytes"]).decode("ascii")
                            await sarvam_ws.transcribe(
                                audio_b64,
                                encoding=encoding,
                                sample_rate=sample_rate,
                            )
                        elif msg.get("text") is not None:
                            data = json.loads(msg["text"])
                            if data.get("type") in {"flush", "end"}:
                                await sarvam_ws.flush()
                            if data.get("type") == "end":
                                break
                except WebSocketDisconnect:
                    pass

            async def receive_transcripts():
                """Forward Sarvam transcript events to the client."""
                try:
                    async for message in sarvam_ws:
                        await websocket.send_json(_sdk_model_dump(message))
                except Exception:
                    pass

            forward_task = asyncio.create_task(forward_audio())
            receive_task = asyncio.create_task(receive_transcripts())
            await forward_task
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(receive_task, timeout=10)
            if not receive_task.done():
                receive_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await receive_task

    except ApiError as e:
        await websocket.send_json({"error": str(e), "status_code": e.status_code})
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()


# ─── TTS REST ───────────────────────────────────────────────────────────────

@app.post("/tts/generate")
async def generate_speech(req: TTSRequest):
    """
    Convert text to speech. Returns audio as a streaming file response.
    Max text length: 2500 characters per request.
    """
    payload = {
        "text": req.text,
        "target_language_code": req.target_language_code,
        "speaker": req.speaker,
        "model": req.model,
        "pace": req.pace,
        "output_audio_codec": req.output_format,
    }
    if req.speech_sample_rate is not None:
        payload["speech_sample_rate"] = req.speech_sample_rate
    if req.temperature is not None:
        payload["temperature"] = req.temperature

    try:
        response = await _sarvam().text_to_speech.convert(**payload)
    except ApiError as exc:
        _raise_sdk_error(exc)

    audio_b64 = response.audios[0]
    audio_bytes = base64.b64decode(audio_b64)

    mime = "audio/wav" if req.output_format == "wav" else f"audio/{req.output_format}"
    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type=mime,
        headers={"Content-Disposition": f"attachment; filename=output.{req.output_format}"},
    )


# ─── Text Translation ───────────────────────────────────────────────────────

@app.post("/text/translate", response_model=TranslateResponse)
async def translate_text(req: TranslateRequest):
    """
    Translate text using the official Sarvam AI SDK quickstart path.
    """
    payload = {
        "input": req.input,
        "source_language_code": req.source_language_code,
        "target_language_code": req.target_language_code,
    }
    for field in ("speaker_gender", "mode", "model", "output_script", "numerals_format"):
        value = getattr(req, field)
        if value is not None:
            payload[field] = value

    try:
        response = await _sarvam().text.translate(**payload)
    except ApiError as exc:
        _raise_sdk_error(exc)

    return TranslateResponse(
        request_id=response.request_id,
        translated_text=response.translated_text,
        source_language_code=response.source_language_code,
    )


# ─── TTS WebSocket (Real-time Streaming) ────────────────────────────────────

@app.websocket("/tts/stream")
async def tts_stream(websocket: WebSocket):
    """
    Real-time streaming TTS via WebSocket.

    Protocol (client → server):
      1. Send JSON config:  {"speaker": "shubh", "target_language_code": "hi-IN", "model": "bulbul:v3"}
      2. Send JSON text chunks: {"text": "नमस्ते, आप कैसे हैं?"}
      3. Send JSON flush:   {"type": "flush"}
      4. Send JSON end:     {"type": "end"}

    Protocol (server → client):
      - Binary audio chunks (WAV PCM)
      - JSON events: {"type": "event", "data": {"event_type": "final"}} when finished
    """
    await websocket.accept()

    try:
        _get_sarvam_api_key()
    except HTTPException:
        await websocket.send_json({"error": "SARVAM_API_KEY not configured"})
        await websocket.close()
        return

    try:
        config_msg = await websocket.receive_text()
        config = json.loads(config_msg)
    except Exception:
        await websocket.send_json({"error": "First message must be a JSON config"})
        await websocket.close()
        return

    try:
        model = config.get("model", "bulbul:v3")
        async with _sarvam().text_to_speech_streaming.connect(
            model=model,
            send_completion_event="true",
        ) as sarvam_ws:
            await sarvam_ws.configure(
                target_language_code=config.get("target_language_code", "hi-IN"),
                speaker=config.get("speaker", "shubh"),
                pace=float(config.get("pace", 1.0)),
                speech_sample_rate=int(config.get("speech_sample_rate", 24000)),
                output_audio_codec=config.get("output_format", "mp3"),
                output_audio_bitrate=config.get("output_audio_bitrate", "128k"),
                min_buffer_size=int(config.get("min_buffer_size", 50)),
                max_chunk_length=int(config.get("max_chunk_length", 150)),
                dict_id=config.get("dict_id"),
            )

            async def forward_text():
                """Forward text chunks from the client through the Sarvam SDK."""
                try:
                    while True:
                        msg = await websocket.receive_text()
                        data = json.loads(msg)
                        if data.get("text"):
                            await sarvam_ws.convert(data["text"])
                        if data.get("type") == "flush":
                            await sarvam_ws.flush()
                        if data.get("type") == "end":
                            await sarvam_ws.flush()
                            break
                except WebSocketDisconnect:
                    pass

            async def receive_audio():
                """Forward generated audio chunks from Sarvam to the client."""
                try:
                    async for message in sarvam_ws:
                        data = _sdk_model_dump(message)
                        if data.get("type") == "audio":
                            audio = base64.b64decode(data["data"]["audio"])
                            await websocket.send_bytes(audio)
                        else:
                            await websocket.send_json(data)
                            if data.get("type") == "event" and data.get("data", {}).get("event_type") == "final":
                                break
                except Exception:
                    pass

            forward_task = asyncio.create_task(forward_text())
            receive_task = asyncio.create_task(receive_audio())
            await forward_task
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(receive_task, timeout=30)
            if not receive_task.done():
                receive_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await receive_task

    except ApiError as e:
        await websocket.send_json({"error": str(e), "status_code": e.status_code})
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
