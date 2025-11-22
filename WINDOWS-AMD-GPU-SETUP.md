# AMD RX 7800 XT GPU Setup Guide for Windows 11

Comprehensive guide for running AI workloads on AMD Radeon RX 7800 XT with Windows 11, including ROCm, DirectML, and various AI frameworks.

## Table of Contents

1. [GPU Compatibility Overview](#gpu-compatibility-overview)
2. [ROCm on Windows 11](#rocm-on-windows-11)
3. [DirectML Setup](#directml-setup)
4. [Ollama Setup for Hypno-Hub](#ollama-setup-for-hypno-hub)
5. [ComfyUI Setup (Image/Video AI)](#comfyui-setup)
6. [InvokeAI Setup](#invokeai-setup)
7. [Troubleshooting](#troubleshooting)
8. [Performance Optimization](#performance-optimization)

---

## GPU Compatibility Overview

### AMD Radeon RX 7800 XT Specifications
- **Architecture**: RDNA 3 (Navi 32)
- **Compute Units**: 60 CUs
- **VRAM**: 16GB GDDR6
- **Memory Bandwidth**: 624 GB/s
- **GFX Version**: gfx1101

### Support Status (2024-2025)

| Platform/Framework | Support Level | Notes |
|-------------------|---------------|-------|
| **ROCm on Windows** | ⚠️ Preview | Officially listed, but preview status |
| **DirectML** | ✅ Full | Best option for Windows 11 |
| **PyTorch (Windows)** | ✅ Supported | ROCm 6.4.4+ |
| **ROCm on Linux** | ✅ Full | Most stable option |
| **WSL2** | ❌ Not Supported | GPU passthrough fails |

---

## ROCm on Windows 11

### Current Status
ROCm for Windows 11 is in **preview** status. The RX 7800 XT is officially supported, but the ecosystem is not as mature as Linux.

### Prerequisites
1. **Windows 11** (fully updated)
2. **Latest AMD Adrenalin Drivers** from [AMD.com](https://www.amd.com/en/support/downloads/drivers.html/graphics/radeon-rx/radeon-rx-7000-series/amd-radeon-rx-7800-xt.html)
3. **Visual Studio 2022** (C++ Build Tools)

### Installation Steps

#### 1. Install AMD Drivers
```powershell
# Download and install latest Adrenalin drivers from AMD website
# Do NOT use Windows Update drivers
```

#### 2. Install HIP SDK (ROCm for Windows)
```powershell
# Download HIP SDK installer from:
# https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html

# Run installer
.\HIP_SDK_installer.exe

# Verify installation
hip-path
hipinfo
```

#### 3. Install PyTorch with ROCm
```powershell
# Create virtual environment
python -m venv rocm_env
.\rocm_env\Scripts\activate

# Install PyTorch with ROCm support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2
```

#### 4. Verify GPU Detection
```python
# test_rocm.py
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
```

### Limitations
- Not all ROCm features available on Windows
- Some ML libraries remain Linux-only
- WSL2 does NOT work with RX 7800 XT
- Primary support is for PyTorch

---

## DirectML Setup

**DirectML is the RECOMMENDED approach for Windows 11** - it's more stable and broadly supported than ROCm on Windows.

### What is DirectML?
Microsoft's DirectML is a GPU-accelerated machine learning API that works across NVIDIA, AMD, and Intel GPUs on Windows. It's built on DirectX 12 and provides excellent AMD GPU support.

### Prerequisites
1. **Windows 11** (updated)
2. **Latest AMD Drivers**
3. **Python 3.10-3.12**

### Installation

#### 1. Install Python and Git
```powershell
# Install Python from python.org or via winget
winget install Python.Python.3.12

# Install Git
winget install Git.Git
```

#### 2. Install torch-directml
```powershell
# Create virtual environment
python -m venv directml_env
.\directml_env\Scripts\activate

# Install torch-directml
pip install torch-directml

# Verify installation
python -c "import torch_directml; print(torch_directml.device())"
```

#### 3. Test GPU Acceleration
```python
# test_directml.py
import torch_directml

device = torch_directml.device()
print(f"DirectML device: {device}")

# Create test tensor on GPU
x = torch.randn(1000, 1000, device=device)
y = torch.randn(1000, 1000, device=device)
z = torch.matmul(x, y)
print(f"Matrix multiplication successful: {z.shape}")
```

---

## Ollama Setup for Hypno-Hub

Ollama is used by Hypno-Hub for AI-powered hypnosis script generation.

### ⚠️ Important Note
**Ollama's AMD GPU support on Windows 11 is experimental**. For production use, Linux is strongly recommended.

### Option 1: Windows Native (Limited GPU Support)

#### Installation
```powershell
# Download Ollama for Windows
# Visit: https://ollama.com/download

# Install the .exe file

# Verify installation
ollama --version
```

#### Testing
```powershell
# Pull a model
ollama pull llama3.2:3b

# Run a test
ollama run llama3.2:3b "Write a short relaxation script"
```

#### Check GPU Detection
```powershell
# Run model and monitor GPU usage
# Open Task Manager -> Performance -> GPU
ollama run llama3.2:3b
```

### Option 2: Windows with HIP SDK (Experimental)

#### Prerequisites
1. Install HIP SDK (see ROCm section above)
2. Set environment variables

```powershell
# Set GPU override for RDNA3
$env:HSA_OVERRIDE_GFX_VERSION = "11.0.0"

# ⚠️ Community script (experimental, use at your own risk)
# Review the script contents before running:
git clone https://github.com/sunfish4951/Install-Ollama-with-AMD-Support-on-Windows.git
cd Install-Ollama-with-AMD-Support-on-Windows
# IMPORTANT: Review install.ps1 contents first, then run:
# .\install.ps1
```

### Option 3: Linux VM/Dual Boot (RECOMMENDED)

For reliable AMD GPU acceleration with Ollama:

1. **Dual Boot** or use a **Linux VM** with GPU passthrough
2. Install Ubuntu 22.04 or 24.04
3. Follow AMD's official ROCm installation guide
4. Install Ollama on Linux:

```bash
# Ubuntu/Debian
curl -fsSL https://ollama.com/install.sh | sh

# Verify GPU detection
rocm-smi
ollama run llama3.2:3b
```

### Recommended Models for 16GB VRAM
- `llama3.2:3b` - Fast, 3B parameters
- `llama3.1:8b` - Balanced, 8B parameters
- `mistral:7b` - Efficient, 7B parameters
- `deepseek-r1:7b` - Reasoning-focused

---

## ComfyUI Setup

ComfyUI is a powerful node-based UI for Stable Diffusion and other AI image/video models.

### Installation with DirectML

#### Option A: Portable Build (Easiest)

```powershell
# 1. Download portable build
# Visit: https://github.com/comfyanonymous/ComfyUI/releases
# Download: ComfyUI_windows_portable_nvidia_or_cpu.7z

# 2. Extract with 7-Zip
# Extract to: C:\ComfyUI

# 3. Install DirectML
cd C:\ComfyUI
.\python_embeded\python.exe -m pip install torch-directml

# 4. Download models
# Place .safetensors files in: ComfyUI\models\checkpoints\
# Popular models:
# - SD 1.5: https://huggingface.co/runwayml/stable-diffusion-v1-5
# - SDXL: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0

# 5. Launch ComfyUI with DirectML
.\run_nvidia_gpu.bat --directml
```

#### Option B: Manual Installation

```powershell
# 1. Clone repository
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 2. Create environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install torch-directml

# 4. For RDNA3 cards, set override if needed
$env:HSA_OVERRIDE_GFX_VERSION = "11.0.0"

# 5. Launch
python main.py --directml
```

### Access ComfyUI
Open browser to: http://127.0.0.1:8188

### Recommended Settings for RX 7800 XT
- **Batch Size**: 1-2
- **Resolution**: 512x512 (SD 1.5) or 1024x1024 (SDXL)
- **Sampler**: DPM++ 2M Karras (fast, high quality)
- **Steps**: 20-30

### Alternative: ComfyUI-Zluda
For potentially better AMD performance:
```powershell
git clone https://github.com/patientx/ComfyUI-Zluda.git
# Follow repo instructions
```

---

## InvokeAI Setup

InvokeAI is a professional-grade Stable Diffusion UI with excellent AMD support via DirectML.

### Installation

```powershell
# 1. Download InvokeAI
# Visit: https://invoke-ai.github.io/InvokeAI/

# 2. Run installer
.\InvokeAI-installer-v4.0.0.exe

# 3. During setup:
# - Select "DirectML" as backend
# - Choose models to download
# - Set installation path

# 4. Launch InvokeAI
cd C:\InvokeAI
.\invoke.bat
```

### First Run Configuration
1. Open web UI: http://localhost:9090
2. Download models from Model Manager
3. Configure settings:
   - Device: DirectML
   - Precision: FP16
   - VRAM: 16GB

### Recommended Models
- **SD 1.5**: Best for speed
- **SDXL**: Best for quality
- **SD 2.1**: Good balance

---

## Troubleshooting

### GPU Not Detected

#### For ROCm:
```powershell
# Check GPU visibility
hipinfo

# If gfx version wrong, override it:
$env:HSA_OVERRIDE_GFX_VERSION = "11.0.0"

# Verify ROCm version
hip-path
```

#### For DirectML:
```python
import torch_directml
print(torch_directml.device())  # Should show "privateuseone:0"
```

### Performance Issues

#### 1. Update Drivers
```powershell
# Always use latest Adrenalin drivers
# Download from AMD.com, not Windows Update
```

#### 2. Enable Hardware Acceleration
```powershell
# In AMD Software:
# Graphics -> Advanced -> Enable "Hardware Acceleration"
```

#### 3. Adjust Power Settings
```powershell
# Windows Power Plan -> High Performance
# AMD Software -> Performance -> Tuning -> Performance
```

### Out of Memory Errors

#### ComfyUI:
```powershell
# Reduce batch size to 1
# Lower resolution (512x512 instead of 1024x1024)
# Enable VAE tiling in advanced settings
```

#### Ollama:
```powershell
# Use smaller models
ollama pull llama3.2:3b  # Instead of :70b

# Set context size limit
ollama run llama3.2:3b --ctx-size 2048
```

### DirectML Crashes

```powershell
# Try different PyTorch/DirectML versions
pip uninstall torch torch-directml
pip install torch-directml==1.13.0

# Or use CPU fallback temporarily:
python main.py --cpu
```

---

## Performance Optimization

### AMD Software Settings

1. **Open AMD Software** (right-click desktop)
2. **Gaming Tab** → **Graphics**:
   - Anti-Aliasing: Application Controlled
   - Texture Filtering: High Performance
3. **Performance** → **Tuning**:
   - Enable Performance Tuning
   - Set GPU Clock to Auto
   - Enable Smart Access Memory (if available)

### Windows Settings

```powershell
# Disable Windows indexing for ComfyUI/models folder
# Settings -> Privacy -> Searching Windows -> Exclude folder

# Set Process Priority (in Task Manager during inference):
# Right-click python.exe -> Set Priority -> High

# Disable background apps:
# Settings -> Privacy -> Background apps -> Off
```

### Model Optimization

#### Use Quantized Models
- **4-bit quantization**: 75% VRAM reduction
- **8-bit quantization**: 50% VRAM reduction

```powershell
# For Ollama (automatic)
ollama pull llama3.2:3b-q4_0  # 4-bit quantized

# For Stable Diffusion
# Use "pruned" or "fp16" versions when available
```

#### Enable VAE Tiling (ComfyUI)
- Reduces VRAM usage for high-res images
- Add "VAE Encode (Tiled)" node

### Monitoring Performance

```powershell
# Task Manager (Ctrl+Shift+Esc)
# Performance -> GPU -> Check utilization

# AMD Software
# Performance -> Metrics -> Overlay Enable
# Shows GPU usage, VRAM, temp in real-time
```

---

## Comparison: ROCm vs DirectML on Windows 11

| Feature | ROCm | DirectML |
|---------|------|----------|
| **Maturity** | Preview/Beta | Stable |
| **AMD Driver Support** | Requires HIP SDK | Built into drivers |
| **Framework Support** | PyTorch mainly | PyTorch, TensorFlow, ONNX |
| **Performance** | ~10% faster (when works) | Excellent |
| **Stability** | ⚠️ Experimental | ✅ Reliable |
| **Ease of Setup** | Complex | Simple |
| **Ollama Support** | Partial | None (CPU fallback) |
| **ComfyUI Support** | Possible | ✅ Excellent |
| **InvokeAI Support** | No | ✅ Excellent |
| **Recommendation** | Linux preferred | **Best for Windows** |

---

## Recommended Setup for Hypno-Hub

### For Windows 11 Users:

1. **Ollama**: Run on **CPU** or use **Linux VM**
   - Windows GPU support is unstable
   - CPU inference still fast for script generation
   
2. **Media Processing**: Use **DirectML**
   - ComfyUI with DirectML for AI image generation
   - Excellent AMD GPU support

3. **Hypno-Hub**: Works out-of-box
   - Ollama will auto-detect best backend
   - Media downloader works natively

### For Linux Users:

1. **Ollama**: Full AMD GPU support
2. **ROCm**: Native, stable, fast
3. **Best performance** for AI workloads

---

## Additional Resources

### Official Documentation
- [AMD ROCm Documentation](https://rocm.docs.amd.com/)
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
- [Microsoft DirectML](https://learn.microsoft.com/en-us/windows/ai/directml/dml-intro)
- [Ollama Documentation](https://github.com/ollama/ollama)

### Community Resources
- [ComfyUI AMD Guide](https://www.kombitz.com/2023/11/14/how-to-install-comfyui-on-windows-with-amd-gpu-using-pytorch-directml/)
- [ROCm GitHub Discussions](https://github.com/ROCm/ROCm/discussions)
- [AMD GPU AI Community](https://www.reddit.com/r/LocalLLaMA/)

### Model Repositories
- [Hugging Face](https://huggingface.co/models)
- [Civitai](https://civitai.com/) (Stable Diffusion models)
- [Ollama Library](https://ollama.com/library)

---

## Quick Start Checklist

- [ ] Install latest AMD Adrenalin drivers
- [ ] Update Windows 11 fully
- [ ] Install Python 3.12
- [ ] Install Git
- [ ] Choose path: DirectML (recommended) or ROCm (advanced)
- [ ] Install torch-directml for DirectML path
- [ ] Install ComfyUI portable build
- [ ] Download Stable Diffusion models
- [ ] Install Ollama for Windows
- [ ] Test Hypno-Hub with Ollama
- [ ] Verify GPU acceleration in Task Manager

---

## Conclusion

**TL;DR for Windows 11 + RX 7800 XT:**

✅ **DirectML** = Best choice for AI image/video (ComfyUI, InvokeAI)  
⚠️ **ROCm** = Experimental, preview status  
🐧 **Linux** = Best for Ollama and LLMs  
💡 **Hypno-Hub** = Works great, CPU inference is fine for script generation

The RX 7800 XT is a powerful GPU with 16GB VRAM, perfect for AI workloads. While ROCm on Windows is improving, DirectML provides the most stable and reliable experience for Windows 11 users in 2024-2025.

For questions or issues, check the [Hypno-Hub repository](https://github.com/Afawfaq/refactored-enigma) or AMD's community forums.

---

**Document Version**: 1.0  
**GPU Tested**: AMD Radeon RX 7800 XT  
**OS**: Windows 11 23H2/24H2  
**ROCm Version**: 6.2-6.4  
**DirectML Version**: 1.13.0+
