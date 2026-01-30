import os
import subprocess
import torch
import shutil
import sys
from moviepy import VideoFileClip

def run_karaoke_process(video_path, output_base_dir="karaoke_output"):
    video_filename = os.path.basename(video_path)
    video_name_no_ext = os.path.splitext(video_filename)[0]
    
    # Demucs uses the filename (minus extension) for its folder structure
    temp_audio_name = f"{video_name_no_ext}_temp"
    temp_audio = os.path.join(output_base_dir, f"{temp_audio_name}.wav")
    
    song_output_dir = os.path.join(output_base_dir, video_name_no_ext)
    os.makedirs(song_output_dir, exist_ok=True)

    try:
        print(f"--- Step 1: Extracting audio from {video_filename} ---")
        video = VideoFileClip(video_path)
        # FIX: Removed 'verbose=False' for MoviePy v2.0 compatibility
        video.audio.write_audiofile(temp_audio, codec='pcm_s16le', logger=None)
        video.close()

        print(f"--- Step 2: Running AI Separation on GPU ---")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        demucs_cmd = [
            sys.executable, "-m", "demucs", 
            "--two-stems", "vocals",
            "-n", "htdemucs",
            "-d", device,
            "-o", song_output_dir,
            temp_audio
        ]
        # Run and wait for completion
        subprocess.run(demucs_cmd, check=True, shell=True)

        # --- Step 3: Organizing output files ---
        print("--- Step 3: Organizing output files ---")
        
        # Path where Demucs placed the files: song_output_dir/htdemucs/temp_audio_name/
        demucs_out_path = os.path.join(song_output_dir, "htdemucs", temp_audio_name)
        
        found_vocals = False
        for stem in ["vocals.wav", "no_vocals.wav"]:
            src = os.path.join(demucs_out_path, stem)
            dst = os.path.join(song_output_dir, stem)
            
            if os.path.exists(src):
                # Using copy + remove is safer on Windows than move when 
                # dealing with recently closed subprocesses
                shutil.copy2(src, dst)
                found_vocals = True

        # Cleanup
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
        
        # Remove the nested Demucs folder structure
        ht_root = os.path.join(song_output_dir, "htdemucs")
        if os.path.exists(ht_root):
            shutil.rmtree(ht_root, ignore_errors=True)

        if found_vocals:
            return True, f"Files saved in: {song_output_dir}"
        else:
            return False, "Separation finished, but files weren't found."

    except Exception as e:
        return False, str(e)