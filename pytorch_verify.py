import torch
import platform

print(f"Platform: {platform.system()}")
print(f"PyTorch version: {torch.__version__}")

if platform.system() == "Windows":
    if torch.cuda.is_available():
        print("CUDA is available")
        print(f"GPU name: {torch.cuda.get_device_name(0)}")
else:
    print('Using MacOS')
    if torch.backends.mps.is_available() and hasattr(torch.backends, 'mps'):
        print("Apple Metal Performance Shaders (MPS) is available")
        print("GPU acceleration: Enabled (Apple Silicon)")
    else:
        print("MPS is not available on this platform")

