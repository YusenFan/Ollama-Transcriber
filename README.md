# Purpose

This project offers a privacy-focused solution for transcribing and summarizing audio recordings through entirely local processing. Using OpenAI's Whisper for transcription and local LLMs via Ollama for summarization, it processes audio files (**MP3/WAV**) entirely on your machine, ensuring sensitive content never leaves your environment.

The tool automatically generates structured summaries including:

- Executive overview
- Detailed content breakdown
- Action items
- Meeting metadata

The project uses a configuration-based approach (config.yaml) for easy customization of output formats, model parameters, and summary structures, making it adaptable for various meeting types and organizational needs

---

## Setup

### Select Python Interpreter Version Between 3.8-3.11

- I am using Python 3.10.11

### Install `ffmpeg` Globally as PowerShell Administrator

**NOTE:** `ffmpeg` **DOES NOT** work in virutal environment and is required for Whisper to work. A "**[Win2]File not found error**" populates when attempting to use within a virtual environment, although  it is not best practice, utilize your global environment instead!

- Follow the instructions [HERE](https://chocolatey.org/install#individual) and install choclatey install via PowerShell Administration to install `ffmpeg`.

- Install FFmpeg:

  ```PowerShell
    choco install ffmpeg
  ```

### Requirements Installation

```bash
python3.10 -m pip install -r requirements.txt --no-warn-script-location
```

### Enable Long Paths

- From PowerShell Administrator run the following:
```bash
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### Download PyTorch with CUDA Support for GPU Acceleration

- If you have NVIDIA GPUs, determine what compute platform you have present:

```bash
  nvidia-smi.exe
```

- Identify "CUDA Version"
- Navigate to: <https://pytorch.org/get-started/locally/>
- Select options specific to your environment and install the command specified!
- Once installation is complete run:

```bash
  python3.10 pytorch_verify.py
```

Example Successfull Output:

- **True**
- **NVIDIA GeForce RTX 3080 Ti Laptop GPU**

---

## Usage

To run the project, use the `main.py` script with the following options:

```bash
python3.10 main.py [OPTIONS]
```

Examples:

Okay, here's the updated table with the commands modified to use `python3.10`:

| Command                                                                | Description                                                                 |
| :--------------------------------------------------------------------- | :-------------------------------------------------------------------------- |
| `python3.10 main.py --gui`                                            | Use the graphical user interface (GUI) to select an audio file.           |
| `python3.10 main.py --audio path/to/recording.mp3`                    | Process a specific audio file with default settings.                      |
| `python3.10 main.py --audio path/to/recording.mp3 --output path/to/output --transcript medium` | Specify the output directory and the Whisper model size for transcription. |
| `python3.10 main.py --audio path/to/recording.mp3 --llm mistral:latest` | Use a specific LLM model for summarization.                               |
| `python3.10 main.py --audio path/to/recording.mp3 --output path/to/summaries --transcript medium --llm mistral:latest` | Full example with all available options.                                  |
| `python3.10 main.py --help` | For more information on the available options

The results of the processing will be stored in a `result` directory created in the same location where you run `main.py`. This directory will contain the following subdirectories:

- `converted_audio/`: Stores the audio files converted to the required format (if necessary).
- `meeting_summaries/`: Contains the generated meeting summary files.
- `transcribed_text/`: Holds the transcriptions of the audio files.

### Customization

1. Download and run your chosen model with Ollama, follow the process [HERE](https://ollama.com/download).
2. Modify the `config.yaml` file located in `src/utils/config.yaml`. You can customize the summarization process by modifying the following key sections:

#### LLM Configuration (`llm:`)

This section allows you to control how the Ollama model generates summaries.

```yaml
llm:
  model_name: "mistral:latest" # Choose your Ollama model (e.g., "mistral:latest")
  # ... other options ...
  options:
    temperature: 0.3 # Controls response creativity (0.0-1.0). Higher values are more creative.
    top_p: 0.5 # Controls similarity sampling (accuracy) when generating a response (0.1-1).
    # ... other options ...
```

- Refer to the [Ollama documentation](https://github.com/ollama/ollama) for details on other available options like `num_ctx`, `num_predict`, `top_k`, `repeat_penalty`, and `num_gpu`.

#### Prompt Configuration (`prompts:`)

This section defines the instructions given to the LLM to generate the summary. You can modify the `summary_prompt` to change the format and content of the summaries.

```yaml
prompts:
  summary_prompt: | # Modify this prompt to customize the summary generation
```