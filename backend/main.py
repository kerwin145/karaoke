from fastapi import FastAPI, UploadFile, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uuid
import os
from audio_processing import run_karaoke_process

app = FastAPI()

tasks = {} # tracks jobs
TRACK_ROOT = "karaoke_output"

def background_wrap(task_id, file_path, original_file_name):
    success, message = run_karaoke_process(file_path, task_id, original_file_name)
    if success:
        tasks[task_id] = {"status":"completed", "message":message}
    else:
        tasks[task_id] = {"status":"failed", "message":message}

    # cleanup the original upload
    if os.path.exists(file_path):
        os.remove(file_path)

@app.post("/upload")
async def process_video(file: UploadFile, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    # Create a unique temp folder or unique prefix for the upload
    os.makedirs("uploads", exist_ok=True)
    temp_path = os.path.join("uploads", f"{task_id}_{file.filename}")  

    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    tasks[task_id] = {"status": "processing", "message": "GPU is working..."}
    
    background_tasks.add_task(background_wrap, task_id, temp_path, file.filename)
    return {"task_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

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