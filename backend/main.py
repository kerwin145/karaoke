from fastapi import FastAPI, UploadFile, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uuid
import os
from audio_processing import run_karaoke_process, run_lyrics_alignment_process
import json
from util import TRACK_ROOT

app = FastAPI()

tasks = {} # tracks jobs

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

def background_wrap(task_id: str, fn, *args, **kwargs):
    try:
        success, message = fn(*args, **kwargs)
        tasks[task_id] = {
            "status": "completed" if success else "failed",
            "message": message
        }
    except Exception as e:
        tasks[task_id] = {"status": "failed", "message": str(e)}

# Video-specific cleanup wrapper
def background_wrap_video(task_id: str, file_path: str, original_file_name: str):
    background_wrap(task_id, run_karaoke_process, file_path, task_id, original_file_name)
    # cleanup the original upload
    if os.path.exists(file_path):
        os.remove(file_path)

# Lyrics-specific wrapper
def background_wrap_lyrics(task_id: str, song_name: str, lyrics: str, language_code: str):
    background_wrap(task_id, run_lyrics_alignment_process, song_name, lyrics, language_code)

@app.post("/upload_track")
async def process_video(file: UploadFile, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    os.makedirs("uploads", exist_ok=True)
    temp_path = os.path.join("uploads", f"{task_id}_{file.filename}")  

    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    tasks[task_id] = {"status": "processing", "message": "GPU is working..."}
    
    background_tasks.add_task(background_wrap_video, task_id, temp_path, file.filename)
    return {"task_id": task_id}

@app.get("/tracks")
async def get_tracks():
    tracks = []
    if os.path.exists(TRACK_ROOT):
        for name in os.listdir(TRACK_ROOT):
            if os.path.isdir(os.path.join(TRACK_ROOT, name)):
                tracks.append(name)
    return {"tracks": tracks}

@app.get("/audio/{song_name}/{track_type}")
async def get_audio_file(song_name: str, track_type: str):
    # track_type should be 'vocals' or 'no_vocals'
    file_path = os.path.join(TRACK_ROOT, song_name, f"{track_type}")
    print(file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio track not found")
        
    return FileResponse(file_path, media_type="audio/wav")

@app.get("/video/{song_name}")
async def get_video_file(song_name: str):
    # Locate the video.mp4 created in audio_processing.py
    file_path = os.path.join(TRACK_ROOT, song_name, "video.mp4")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
        
    return FileResponse(file_path, media_type="video/mp4")

@app.get("/lyrics/{song_name}")
async def get_lyrics_data(song_name: str):
    alignment_path = os.path.join(TRACK_ROOT, song_name, "alignment.json")
    lyrics_path = os.path.join(TRACK_ROOT, song_name, "lyrics_raw.txt")

    # Check files exist before trying to open them
    if not os.path.isfile(alignment_path) or not not os.path.isfile(lyrics_path) :
        return None
    
    with open(alignment_path, "r", encoding="utf-8") as f:
        alignment_data = json.load(f)
    with open(lyrics_path, "r", encoding="utf-8") as f:
        lyrics_raw = f.read()

    return {
        "song_name": song_name,
        "language": alignment_data["language"],
        "lyrics_raw": lyrics_raw,
        "word_segments": alignment_data["word_segments"]
    }

@app.post("/upload_lyrics/{song_name}")
async def process_lyrics(song_name: str, background_tasks: BackgroundTasks, lyrics: str = Form(...), language_code: str = Form("en")):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "message": "Aligning lyrics..."}
    background_tasks.add_task(background_wrap_lyrics, song_name, lyrics, language_code)
    return {"task_id": task_id}