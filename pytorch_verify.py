import torch
import platform

print(f"Platform: {platform.system()}")
print(f"PyTorch version: {torch.__version__}")

if torch.cuda.is_available():
    print("CUDA is available")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    print("Apple Metal Performance Shaders (MPS) is available")
    print("GPU acceleration: Enabled (Apple Silicon)")
else:
    print("No GPU acceleration available - will use CPU")