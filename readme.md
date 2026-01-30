# Create the environment
```conda create -n karaoke python=3.10 -y```
```conda activate karaoke```

# Set Strict Channel Priority (This is the magic fix)
# This forces Conda to ONLY use one channel for a package even if another has a newer version
```conda config --env --add channels conda-forge```
```conda config --env --set channel_priority strict```

```conda install -c pytorch -c nvidia -c conda-forge pyside6=6.8.1 pytorch torchvision torchaudio pytorch-cuda=12.4 ffmpeg libffi -y```

# to test
```python -c "import _ctypes; import torch; print('\n' + ' SUCCESS '.center(30, '=')); print(f'GPU: {torch.cuda.get_device_name(0)}'); print(f'Torch CUDA: {torch.version.cuda}'); print('='*30)"```

# last remaining installs
```pip install demucs pyqtdarktheme soundfile moviepy```

Or just try using the install from the environment.yml