# Checkpoint Prompt

We are developing a Python-based audio transcription and summarization tool.  Our goal is to create a robust and user-friendly application that can process audio files, transcribe them using Whisper, and generate summaries using a local LLM (Ollama).  We also aim to make the tool easily integratable with UI's like OpenWebUI.

**Project Structure:**

## Project Directory Structure:
├── ./
    ├── main.py
    ├── README.md
    ├── requirements.txt
    ├── src/
        ├── __init__.py
        ├── audio/
            ├── converter.py
            ├── preprocess.py
            ├── __init__.py
        ├── summary/
            ├── summarize.py
            ├── __init__.py
        ├── transcription/
            ├── transcribe.py
            ├── transcribe_cli.py
            ├── __init__.py
        ├── utils/
            ├── config.py
            ├── config.yaml
            ├── __init__.py

The project consists of several Python modules:

*   `main.py`: The main script that orchestrates the entire workflow.
*   `src/utils/config.py`: Handles configuration loading and validation from `config.yaml`.
*   `src/audio/converter.py`: Handles audio format conversion using FFmpeg.
*   `src/transcription/transcribe.py`: Handles audio transcription using the Whisper model.
*   `src/summary/summarize.py`: Handles text summarization using Ollama.

**Key Functionality and Progress:**

1.  **Configuration:** We have implemented a `ConfigManager` in `config.py` to load and validate settings from `config.yaml`.  This includes paths to audio files, output directories, LLM settings, and document formatting options.

2.  **Logging:** We have set up logging using Python's `logging` module to track the application's progress and handle errors.

3.  **Audio Conversion:** The `convert_audio` function in `converter.py` handles audio format conversion using FFmpeg.  It checks if conversion is necessary and performs it if needed.

4.  **Whisper Transcription:** The `transcribe_audio` function in `transcribe.py` uses the Whisper model (loaded with `whisper.load_model`) to transcribe audio files.  It handles model loading, device selection (CPU or CUDA), and saving the transcription to a text file.

5.  **Summarization (Refactored):** The `summarize.py` module contains the `TranscriptProcessor` class, which handles the summarization logic.  We have refactored this module significantly. Key functions include `read_transcript()`, `generate_llm_response()`, `generate_summary()`, `generate_summaries()`, `format_document()`, and `save_document()`. These functions handle reading the transcript, interacting with the Ollama LLM, generating summaries, formatting the document, and saving the document respectively.

6.  **`main.py` Integration:** The `main.py` script now correctly integrates with the refactored `summarize.py` module.  It initializes the `TranscriptProcessor`, reads the transcript using the correct path from the config, calls the appropriate methods, and saves the document to the correct output directory (also from the config). It also imports and utilizes the `get_audio_duration` and `generate_metadata` functions.

**Next Steps:**

We are about to add functionality to `main.py` to allow the user to specify the audio file in one of two ways:

1.  **Command-line argument:** `main.py [audio_file.mp3]`
2.  **File system viewer:** A graphical way to browse and select the audio file.

We will use Python's `argparse` for command-line arguments and either `tkinter` or `PyQt` for the file dialog.  We will choose between `tkinter` (simpler) or `PyQt` (more powerful) based on your preference.  We will ensure that the core logic remains separate from the input handling for easy UI integration in the future.

**Current Status:** The code is functional and can process audio files, transcribe them, and generate summaries. The main.py correctly integrates with the refactored summarize.py module.  We are ready to add the command-line and file dialog input options.