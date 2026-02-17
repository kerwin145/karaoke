# Create the env
```conda env create -f environment.yml```

or

```conda env update --file environment.yml```

# Running the thing
## Backend
(C:\miniconda3\shell\condabin\conda-hook.ps1) ; (conda activate karaoke_pro)
(C:\ProgramData\miniconda3\shell\condabin\conda-hook.ps1) ; (conda activate karaoke_pro)
cd .\backend\
uvicorn main:app --reload

# Frontend
cd frontend
& C:/ProgramData/miniconda3/envs/karaoke_pro/python.exe main.py
or
& C:/miniconda3/envs/karaoke_pro/python.exe main.py