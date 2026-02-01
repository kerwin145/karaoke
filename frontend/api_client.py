import requests

BASE_URL = "http://127.0.0.1:8000"

def upload_to_server(file_path):
    url = f"{BASE_URL}/upload"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    return response.json() # Returns {"task_id": "..."}

def check_status(task_id):
    url = f"{BASE_URL}/status/{task_id}"
    response = requests.get(url)
    return response.json() # Returns {"status": "processing/completed/failed", ...}

def get_all_tracks():
    try:
        # Added a 3-second timeout so the UI doesn't freeze if server is dead
        response = requests.get(f"{BASE_URL}/tracks", timeout=3)
        response.raise_for_status() # Raises error for 4xx or 5xx codes
        return response.json().get("tracks", [])
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        return [] # Return empty list so the UI doesn't crash