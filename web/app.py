import asyncio
import json
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, str(Path(__file__).parent.parent))
from transcriber.core import is_url, transcribe

app = FastAPI(title="Video Transcriber")

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

jobs: dict = {}


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/transcribe")
async def start_transcription(
    background_tasks: BackgroundTasks,
    source_type: str = Form(...),
    url: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    model: str = Form("base"),
    output_format: str = Form("txt"),
    language: Optional[str] = Form(None),
):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued", "status_text": "Queued", "result": None, "error": None}

    lang = language or None

    if source_type == "url":
        if not url:
            raise HTTPException(400, "URL required")
        background_tasks.add_task(_run_url_job, job_id, url, model, output_format, lang)
    else:
        if not files:
            raise HTTPException(400, "Files required")
        tmp = tempfile.mkdtemp()
        saved = []
        for f in files:
            dest = os.path.join(tmp, f.filename)
            content = await f.read()
            with open(dest, 'wb') as fp:
                fp.write(content)
            saved.append(dest)
        background_tasks.add_task(_run_file_job, job_id, saved, model, output_format, lang, tmp)

    return {"job_id": job_id}


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    async def generate():
        while True:
            job = jobs.get(job_id)
            if not job:
                yield f"data: {json.dumps({'status': 'error', 'error': 'Job not found'})}\n\n"
                break
            yield f"data: {json.dumps(job)}\n\n"
            if job["status"] in ("done", "error"):
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(generate(), media_type="text/event-stream")


def _set_progress(job_id: str, text: str):
    if job_id in jobs:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["status_text"] = text.capitalize()


def _run_url_job(job_id, url, model, output_format, language):
    try:
        result = transcribe(
            url, model_size=model, output_format=output_format, language=language,
            progress_callback=lambda msg: _set_progress(job_id, msg),
        )
        jobs[job_id] = {"status": "done", "status_text": "Done", "result": result, "error": None}
    except Exception as e:
        jobs[job_id] = {"status": "error", "status_text": "Error", "result": None, "error": str(e)}


def _run_file_job(job_id, paths, model, output_format, language, tmp_dir):
    try:
        results = []
        for i, path in enumerate(paths):
            def cb(msg, idx=i): _set_progress(job_id, f"File {idx+1}/{len(paths)}: {msg}")
            result = transcribe(
                path, model_size=model, output_format=output_format, language=language,
                progress_callback=cb,
            )
            name = Path(path).stem
            results.append(f"=== {name} ===\n{result}" if len(paths) > 1 else result)
        jobs[job_id] = {"status": "done", "status_text": "Done", "result": "\n\n".join(results), "error": None}
    except Exception as e:
        jobs[job_id] = {"status": "error", "status_text": "Error", "result": None, "error": str(e)}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
