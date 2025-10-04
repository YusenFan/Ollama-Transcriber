# Purpose

This project offers a privacy-focused solution for transcribing and summarizing audio recordings through entirely local processing on you. Using OpenAI's Whisper for transcription and local LLMs via Ollama for summarization, it processes audio files (**MP3/WAV**) entirely on your machine, ensuring sensitive content never leaves your environment.

The tool automatically generates structured summaries including:

- Executive overview
- Detailed content breakdown
- Action items
- Meeting metadata

**NOTE:** This project is currently functional and tested on Macos Tahoe 26.0

---

## Setup

### Select Python Interpreter Version Between 3.8-3.11

- I am using Python 3.10.11

### Install `ffmpeg` Globally 

**NOTE:** `ffmpeg` **DOES NOT** work in virutal environment and is required for Whisper to work. A "**[Win2]File not found error**" is thrown when attempting to use within a virtual environment, although  it is not best practice, utilize your global environment instead.


- Install FFmpeg:

  ```PowerShell
    brew install ffmpeg
  ```

  #### Install PyTorch

For Apple Silicon (M1/M2/M3):
```bash
pip3 install torch torchvision torchaudio
```

PyTorch will automatically use Metal Performance Shaders (MPS) for GPU acceleration on Apple Silicon.

### Requirements Installation

```bash
python3.10 -m pip install -r requirements.txt --no-warn-script-location
```

#### Verify Setup

```bash
python3 pytorch_verify.py
```

Expected output for Apple Silicon:
- Platform: Darwin
- PyTorch version: [version]
- Apple Metal Performance Shaders (MPS) is available

---

## Usage

### LLM Customization

- [Install Ollama on your system](https://ollama.com/download) and select model.
- Modify the **`config.yaml`** file located in **`src/utils/config.yaml`** and specify the model that you've downloaded.
- Refer to the [Ollama documentation](https://github.com/ollama/ollama/tree/main/docs) for details on other available options like `num_ctx`, `num_predict`, `top_k`, `repeat_penalty`, and `num_gpu`.

```yaml
llm:
  model_name: "mistral:latest" # Choose your Ollama model (e.g., "mistral:latest")
  # ... other options ...
  options:
    temperature: 0.3 # Controls response creativity (0.0-1.0). Higher values are more creative.
    top_p: 0.5 # Controls similarity sampling (accuracy) when generating a response (0.1-1).
    # ... other options ...
```

### Begin Ollama Server

```bash
ollama serve
```

### Run Project

To run the project, use the `main.py` script with the following options:

```bash
python3.10 main.py [OPTIONS]
```

| Command                                                                | Description                                                                 |
| :--------------------------------------------------------------------- | :-------------------------------------------------------------------------- |
| `python3.10 main.py --gui`                                            | Use the graphical user interface (GUI) to select an audio file.           |
| `python3.10 main.py --audio path/to/recording.mp3`                    | Process a specific audio file with default settings.                      |
| `python3.10 main.py --audio path/to/recording.mp3 --output path/to/output --transcript medium` | Specify the output directory and the Whisper model size for transcription. |
| `python3.10 main.py --audio path/to/recording.mp3 --llm mistral:latest` | Use a specific LLM model for summarization.                               |
| `python3.10 main.py --audio path/to/recording.mp3 --output path/to/summaries --transcript medium --llm mistral:latest` | Full example with all available options.                                  |
| `python3.10 main.py --help` | For more information on the available options |

The results of the processing will be stored in a `results` directory created in the same location where you run `main.py`. This directory will contain the following subdirectories:

- `converted_audio/`: Stores the audio files converted to the required format (if necessary).
- `meeting_summaries/`: Contains the generated meeting summary files.
- `transcribed_text/`: Holds the transcriptions of the audio files.

### System Prompt Customization

- Modify the `config.yaml` file located in `src/utils/config.yaml`. You can customize the summarization process by modifying the following sections:

```yaml
prompts:
  summary_prompt: | # Modify this prompt to customize the summary generation
    Analyze the provided transcript and create a comprehensive Summary Report that captures all essential information.

    Structure the summary as follows:

    1. **EXECUTIVE OVERVIEW**
    - Synthesize core meeting purpose and outcomes
    - ... (more details)

    2. **KEY DISCUSSION POINTS**
    - Present main topics chronologically with timestamps
    - ... (more details)

    3. **ACTION ITEMS AND RESPONSIBILITIES**
    - List concrete tasks with clear ownership and deliverables
    - ... (more details)

    4. **CONCLUSIONS AND NEXT STEPS**
    - Summarize achieved outcomes against objectives
    - ... (more details)

    Format Guidelines:
    - Use clear, professional language ...
    - ... (more guidelines)
```
