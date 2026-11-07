#!/bin/zsh
cd "$(dirname "$0")" || exit 1
if ! command -v ffmpeg >/dev/null || ! command -v ffprobe >/dev/null; then
 echo 'Instala FFmpeg con: brew install ffmpeg';read;exit 1
fi
if [ ! -d .venv ]; then
 python3 -m venv .venv || exit 1
 .venv/bin/python -m pip install -r requirements.txt || exit 1
fi
 echo 'ReelStudio V2: http://127.0.0.1:8766'
.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8766
