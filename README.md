# Meeting Transcriber

## Prerequisites

### Open VSCode as Local User

- **Select Python Interpreter version between 3.8-3.11**
  - I am using Python 3.10.11

### Install ffmpeg Globally as PowerShell Administrator

**NOTE:** ffmpeg seems to not work in virutal environment (a [Win2]File not found error continues to populate when attempting to use within a virtual environment), although is it not best practice, utilize your global environment instead!

- Install choclatey install via PowerShell Administration shell: <https://chocolatey.org/install#individual>
  - choco install ffmpeg

### Download Whisper from [GitHub](https://github.com/openai/whisper/tree/main#setup)

- pip install git+<https://github.com/openai/whisper.git>
- pip install setuptools-rust
- pip install pydub (used to read .mp3 files)

### Download PyTorch with CUDA Support (for GPU Acceleration) - OPTIONAL

- If you have NVIDIA GPUs, determine what compute platform you have present:

```bash
  nvidia-smi.exe
```

- Identify "CUDA Version"
- Navigate to: <https://pytorch.org/get-started/locally/>
- Select options specific to your environment and install the command specified!
- Once installation is complete run:

```bash
  python3.X pytorch_verify.py
```

Example Successfull Output:

- **True**
- **NVIDIA GeForce RTX 3080 Ti Laptop GPU**

### Install Java Installation

- To use the meeting transcriber effectively, ensure that Java is installed on your system. This is required for certain functionalities, such as grammar checking with `language-tool-python`.

1. **Uninstall Existing Java Versions:**
   - Navigate to Control Panel > Programs > Programs and Features.
   - Uninstall any existing Java installations by selecting them and clicking "Uninstall."

2. **Download Java:**
   - Visit the [Oracle Java Downloads](https://www.oracle.com/java/technologies/javase-jdk11-downloads.html) page or [OpenJDK](https://openjdk.java.net/) for an open-source version.
   - Download the appropriate installer for your operating system (e.g., Windows x64).

3. **Install Java:**
   - Run the downloaded installer.
   - Follow the installation prompts, ensuring that you select options to set up environment variables automatically if prompted.
   - The installation should create a `\bin` directory inside the Java installation folder (e.g., `C:\Program Files\Java\jdk-<version>\bin`).

### Verify Java Installation

1. **Check Java Version:**

    ```bash
    java -version
    ```

2. **Set Environment Variables (if needed):**
   - If `java -version` does not work, you may need to manually set the `JAVA_HOME` environment variable and update the `Path`.
   - Open System Properties > Environment Variables.
   - Add a new system variable named `JAVA_HOME` with the path to your JDK directory (e.g., `C:\Program Files\Java\jdk-<version>`).
   - Edit the `Path` variable and add `%JAVA_HOME%\bin`.

## Tool Usage

### 1. `pytorch_verify.py`

### 2. `transcribe-args.py` or `transcribe.py`

The script supports two modes of operation: single file transcription and multiple files (batch) transcription.

#### Command Line Arguments

- `-h` or `--help`: To see all available options and examples

- `--mode`: **REQUIRED**. Choose between 'single' or 'multiple'
  - 'single': Transcribe one audio file
  - 'multiple': Transcribe all audio files in a directory

- `--input-file`: Path to the audio file (**REQUIRED** when mode is 'single')

- `--input-dir`: Path to directory containing audio files (**REQUIRED** when mode is 'multiple')

- `--output-dir`: **REQUIRED**. Directory where transcription files will be saved

- `--model`: **OPTIONAL**. Choose Whisper model size (If not specified, the script uses the 'base' model by default.)
  - Options: 'tiny', 'base', 'small', 'medium', 'large'

### Model Selection

The `--model` argument determines the Whisper model to use:

- `tiny`: Fastest, lowest accuracy
- `base`: Good balance of speed and accuracy
- `small`: Better accuracy, slower than base
- `medium`: High accuracy, slower
- `large`: Highest accuracy, slowest

### Examples

#### Single File Transcription

```bash
python transcribe.py --mode single \
                    --input-file path/to/audio.mp3 \
                    --output-dir path/to/output \
                    --model large
```

#### Multiple Files Transcription

```bash
python transcribe.py --mode multiple \
                    --input-dir path/to/audio/files \
                    --output-dir path/to/output \
                    --model base
```

### Output

- For single file mode: Creates a .txt file with the same name as the input audio file
- For multiple files mode: Creates a .txt file for each audio file in the input directory

## Supported Audio Formats

- MP3
- WAV

## 3. `postprocess.py`
