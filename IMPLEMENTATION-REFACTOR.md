**Implementation Guide: Meeting Transcriber (Single Entry Point)**

This guide outlines the steps to refactor your project, making `main.py` the sole script the user interacts with.

**1. Refactor `transcribe.py` (Transcription Module):**

*   **Core Transcription Logic:** `transcribe.py` will contain *only* the functions related to the core transcription process.  These functions should be designed to be reusable and independent of user interaction or file I/O.
*   **Key Functions:**
    *   `load_model(model_name, device)`: Loads the Whisper model.  The `model_name` should be passed as an argument, *not* obtained via user input.
    *   `transcribe_audio_chunk(audio_chunk, model)`: Transcribes a single audio chunk.
    *   `process_audio_chunks(audio_np, model, chunk_size, overlap, sample_rate)`: Processes the entire audio (NumPy array), divides it into chunks, and calls `transcribe_audio_chunk` for each chunk.  It should *not* handle audio loading or preprocessing.
    *   `transcribe_audio(audio_path, config)`: *This is the main entry point for transcription*.  It takes the audio file path and a configuration dictionary as input.  It loads the model (using `load_model`), calls `preprocess_audio` (from `preprocess.py`), calls `process_audio_chunks`, and *returns* the complete transcribed text as a string.
*   **No User Interaction or File I/O:**  `transcribe.py` should *not* contain any `input()` calls, `print()` statements related to user interaction, or file I/O operations for *saving* the transcription.

**2. Refactor `summarize.py` (Summarization Module):**

*   **Summarization Logic:** `summarize.py` remains largely the same.  It contains the functions for generating summaries.
*   **Key Functions:**  (As you've already defined them)
    *   `generate_metadata()`: Generates metadata for the document.
    *   `TranscriptProcessor`:  A class to handle transcript summarization.
    *   `get_audio_duration()`:  Gets the duration of the audio.
*   **Input and Output:** The `TranscriptProcessor` should accept the transcribed text as a string argument to its `process_and_save_summary` function (or equivalent).  It should return the path to the saved summary file.

**3. Refactor/Create `main.py` (Main Orchestration Script):**

*   **Single Entry Point:** `main.py` will be the *only* script the user runs.
*   **Workflow Orchestration:** It will handle the entire workflow:
    1.  Parse command-line arguments (using `argparse`).  At a minimum, it should accept the audio file path as an argument.  It can also accept optional arguments for configuration file, output directory, etc.
    2.  Load the configuration (from `config.yaml` or a path specified by a command-line argument).  This configuration should contain settings for audio conversion, transcription, and summarization.
    3.  Convert the audio (if necessary) using `convert_audio` (from `audio_converter.py`).
    4.  Call `transcribe_audio` (from `transcribe.py`) to transcribe the audio.  Pass the audio file path and the configuration to this function.
    5.  Call the summarization functions (from `summarize.py`) to generate the summary.  Pass the transcribed text to the summarization function.
    6.  Handle all file I/O: Save the transcription and the summary to files in the specified output directory.
*   **Error Handling:**  Include robust error handling to catch potential issues during conversion, transcription, or summarization.

**4. Update `config.yaml`:**

*   **Comprehensive Settings:**  Ensure `config.yaml` contains *all* the necessary settings for each stage of the process:
    *   Audio conversion settings (output format).
    *   Transcription settings (model, chunk size, overlap).
    *   Summarization settings (LLM model, prompts, output format, metadata fields).

**5. Update `requirements.txt`:**

*   **All Dependencies:**  Make sure `requirements.txt` lists *all* required Python packages.

**Workflow:**

The user will run `main.py`, providing the audio file path (and any other optional arguments).  `main.py` will then handle the entire process behind the scenes, from conversion to summarization, using the functions in the other modules.  This approach provides a clean separation of concerns while keeping the user interaction simple.
