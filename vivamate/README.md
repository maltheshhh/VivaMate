# VivaMate
Local-first AI placement-prep chatbot (FastAPI + SQLite + Ollama + faster-whisper).

## Run
1. Install [Ollama](https://ollama.com), then `ollama pull qwen2.5:7b`
2. `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
3. `cp .env.example .env` (leave blank for fully local; `VIVAMATE_MODEL` defaults to `qwen2.5:7b`)
4. `uvicorn main:app --port 8000` and open http://localhost:8000
5. Click **Setup**, add name, role, GitHub username, resume PDF.

## Optional cloud fallback
Set `VIVAMATE_API_KEY`, `VIVAMATE_API_BASE` (e.g. `https://api.openai.com/v1`) and `VIVAMATE_MODEL` in `.env`, restart, then pick **Cloud** in Settings. The key never leaves the server.

## Offline test
1. Run once online so the Whisper `base` model downloads (first mic use).
2. Turn Wi-Fi off. The header badge should read **Offline and working**.
3. Send a message, use the mic, and check the Readiness gauge. Everything runs on localhost.
(GitHub repo ingest needs internet at setup time only.)
