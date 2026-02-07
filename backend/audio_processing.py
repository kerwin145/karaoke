import os
import subprocess
import torch
import shutil
import sys
from moviepy import VideoFileClip

def run_karaoke_process(video_path, task_id, original_file_name, output_base_dir="karaoke_output"):
    video_name_no_ext = os.path.splitext(original_file_name)[0]
    
    # Demucs uses the filename (minus extension) for its folder structure
    temp_audio_name = f"temp_{task_id}"
    temp_audio = os.path.join(output_base_dir, f"{temp_audio_name}.wav")
    
    song_output_dir = os.path.join(output_base_dir, video_name_no_ext)
    os.makedirs(song_output_dir, exist_ok=True)

    try:    
        print(f"--- Step 1: Extracting audio from {original_file_name} ---")
        video = VideoFileClip(video_path)

        video.audio.write_audiofile(temp_audio, codec='pcm_s16le', logger=None)
        muted_video_path = os.path.join(song_output_dir, "video.mp4")
        video.write_videofile(muted_video_path, audio=False, logger=None)
        
        video.close()

        print(f"--- Step 2: Running AI Separation on GPU ---")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        demucs_cmd = [
            sys.executable, "-m", "demucs", 
            "--two-stems", "vocals",
            # "-n", "htdemucs",
            "-n", "htdemucs_ft",
            "-d", device,
            # "--shifts", "3", 
            "-o", output_base_dir,
            temp_audio
        ]

        # Run and wait for completion
        subprocess.run(demucs_cmd, check=True, shell=True)

        # --- Step 3: Organizing output files ---
        print("--- Step 3: Organizing output files ---")

        demucs_out_path = os.path.join(output_base_dir, "htdemucs_ft", temp_audio_name)
        
        found_vocals = False
        for stem in ["vocals.wav", "no_vocals.wav"]:
            src = os.path.join(demucs_out_path, stem)
            dst = os.path.join(song_output_dir, stem)

            if os.path.exists(src):
                shutil.copy2(src, dst)
                found_vocals = True

        # Cleanup
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
        
        # Remove the nested Demucs folder structure
        ht_root = os.path.join(output_base_dir, "htdemucs_ft") 

        if os.path.exists(ht_root):
            shutil.rmtree(ht_root, ignore_errors=True)

        # last thing is to save the video (without audio)

        print("Processing done")

        if found_vocals:
            return True, f"Files saved in: {song_output_dir}"
        else:
            return False, "Separation finished, but files weren't found."

    except Exception as e:
        print(f"Error encountered: {e}")
        if os.path.exists(song_output_dir):
            shutil.rmtree(song_output_dir, ignore_errors=True)
        return False, str(e)
    
    finally:
        print("--- Step 4: Finalizing Cleanup ---")
        # 1. Remove the temporary WAV file extracted from video
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
        
        # 2. Remove the nested 'htdemucs_ft' directory entirely
        if os.path.exists(ht_root):
            shutil.rmtree(ht_root, ignore_errors=True)