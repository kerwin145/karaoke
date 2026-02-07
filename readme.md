# Create the env
```conda env create -f environment.yml```

or

```conda env update --file environment.yml```

# Running the thing
## Backend
cd backend
conda activate karaoke_pro
uvicorn main:app --reload

# Frontend
cd frontend
& C:/ProgramData/miniconda3/envs/karaoke_pro/python.exe main.py