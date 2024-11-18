import whisper
import torch
import os
import sys
import warnings
import numpy as np
import math
from pydub import AudioSegment
from preprocess import preprocess_audio


# Suppress FutureWarning associated with torch.load
warnings.filterwarnings("ignore", category=FutureWarning)

def strip_quotes(path):
    """
    Remove leading and trailing quotes from a string.
    """
    return path.strip('"\'')

def load_model():

    """
    Prompt the user to select a Whisper model and specify GPU if available.
    """

    #NOTE: Change to command line args.... rather than options for the user to select....

    #NOTE: Select large model to potential improve transcription output!

    models = ["tiny", "base", "small", "medium", "large"]
    print("Available Whisper models:")
    for i, model_name in enumerate(models, 1):
        print(f"{i}. {model_name}")
    
    while True:
        try:
            choice = int(input("Select a model (1-5): "))
            if 1 <= choice <= 5:
                model_name = models[choice - 1]
                break
            else:
                print("Invalid choice. Please select a number between 1 and 5.")

        except ValueError:
            print("Invalid input. Please enter a number.")

    # Check if GPU (CUDA) is available, otherwise use CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading model on {device}...")
    
    # Load the model onto the specified device (GPU or CPU)
    model = whisper.load_model(model_name, device=device)
    
    return model

#NOTE: You can modify overlap here to provide context to ensure transcription avoids repeat of words.
def process_audio_chunks(file_path, model, chunk_size=30, overlap=4): 
    """
    Process audio file by chunks and return the transcription with improved overlap handling.
    Adds overlap between chunks to provide better transcription context.
    """
    try:
        # Load and preprocess the audio file
        print(f"Attempting to load audio file: {file_path}")
        audio_segment = preprocess_audio(file_path)  # Use preprocessed audio
        
        sample_rate = audio_segment.frame_rate
        audio_np = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
        audio_np = audio_np / np.max(np.abs(audio_np))  # Normalize to [-1, 1]
        
        # Compute the number of chunks
        target_sample_rate = 16000
        num_chunks = math.ceil(len(audio_np) / (chunk_size * target_sample_rate))
        print(f"Number of chunks: {num_chunks}")

        transcript = []
        for i in range(num_chunks):
            # Calculate start and end indices with overlap
            start = int(i * chunk_size * target_sample_rate) - int(overlap * target_sample_rate)
            start = max(0, start)  # Ensure start is not negative
            end = int((i + 1) * chunk_size * target_sample_rate)

            # Extract audio chunk with overlap
            audio_chunk = audio_np[start:end]

            # Ensure the chunk is not empty
            if len(audio_chunk) == 0:
                continue

            print(f"Transcribing chunk {i+1}/{num_chunks}...")

            # Transcribe each audio chunk
            chunk_transcript = transcribe_audio_chunk(audio_chunk, model)

            if chunk_transcript:
                print(f"Chunk {i+1} transcription: {chunk_transcript}")
                transcript.append(chunk_transcript)

        return ' '.join(transcript)
    except Exception as e:
        print(f"Error processing audio chunks: {e}")
    return None

#Transcribes a single audio chunk
def transcribe_audio_chunk(audio_chunk, model):
    try:
        if isinstance(audio_chunk, np.ndarray):
            audio_chunk = torch.tensor(audio_chunk, dtype=torch.float32).unsqueeze(0)
        
        audio_chunk = audio_chunk.squeeze().numpy()
        
        print(f"Chunk duration: {len(audio_chunk) / 16000:.2f} seconds")
        print(f"Chunk amplitude range: {np.min(audio_chunk):.4f} to {np.max(audio_chunk):.4f}")
        
        result = model.transcribe(audio_chunk, language="en", temperature=0.0)
        return result['text']
    except Exception as e:
        print(f"Error transcribing audio chunk: {e}")
    return None

def process_audio_chunks(file_path, model, chunk_size=20, overlap=2):
    """
    Process audio file by chunks and return the transcription.
    Adds overlap between chunks to provide better transcription context.
    """
    try:
        # Load the audio file using pydub
        print(f"Attempting to load audio file: {file_path}")
        audio_segment = AudioSegment.from_file(file_path)
        sample_rate = audio_segment.frame_rate

        # Convert audio to numpy array and normalize
        audio_np = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
        audio_np = audio_np / np.max(np.abs(audio_np))  # Normalize to [-1, 1]
        print(f"Audio normalized. Sample data range: {np.min(audio_np)} to {np.max(audio_np)}")

        # Resample audio to 16kHz (16000 Hz)
        target_sample_rate = 16000
        if sample_rate != target_sample_rate:
            print(f"Resampling audio from {sample_rate} Hz to {target_sample_rate} Hz")
            audio_segment = audio_segment.set_frame_rate(target_sample_rate)
            sample_rate = target_sample_rate
            audio_np = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
            audio_np = audio_np / np.max(np.abs(audio_np))  # Normalize again after resampling

        # Convert numpy array to torch tensor and reshape
        audio = torch.tensor(audio_np, dtype=torch.float32).unsqueeze(0)
        print("Audio file loaded and converted to tensor successfully")

        # Compute the number of chunks
        num_chunks = math.ceil(len(audio[0]) / (chunk_size * sample_rate))
        print(f"Number of chunks: {num_chunks}")

        transcript = []
        for i in range(num_chunks):
            # Calculate start and end indices with overlap
            start = int(i * chunk_size * sample_rate) - int(overlap * sample_rate)
            start = max(0, start)  # Ensure start is not negative
            end = int((i + 1) * chunk_size * sample_rate)
            
            audio_chunk = audio[:, start:end]

            # Ensure the chunk is not empty
            if audio_chunk.size(1) == 0:
                continue

            # Convert tensor to numpy array
            audio_chunk = audio_chunk.squeeze().numpy()
            print(f"Audio chunk {i+1}/{num_chunks} converted to numpy array. Data range: {np.min(audio_chunk)} to {np.max(audio_chunk)}")

            # Transcribe each audio chunk
            print(f"Transcribing chunk {i+1}/{num_chunks}...")

            chunk_transcript = transcribe_audio_chunk(audio_chunk, model)

            if chunk_transcript:
                print(f"Chunk {i+1} transcription: {chunk_transcript}")
                transcript.append(chunk_transcript)

        return ' '.join(transcript)
    except Exception as e:
        print(f"Error processing audio chunks: {e}")
    return None

# Sanity check to ensure that your file is accessible to be read!

def check_file_properties(file_path):
    try:
        print(f"Checking properties for file: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        print(f"File is readable: {os.access(file_path, os.R_OK)}")
        print(f"File size: {os.path.getsize(file_path)} bytes")

    except Exception as e:

        print(f"Error checking file properties: {e}")

def is_file_accessible(file_path):
    return os.path.exists(file_path) and os.access(file_path, os.R_OK)

def transcribe_single_file(input_file, output_dir, model):  # Add 'model' parameter here
    try:
        check_file_properties(input_file)
        
        print(f"Transcribing {input_file}...")

        # Adjust chunk size and overlap as needed (chunk_size: 30s is ideal for Whisper, overlap: between 0.5 to 2 secs)
        transcript = process_audio_chunks(input_file, model, chunk_size=20, overlap=2)  # Pass 'model' here
        
        if transcript is None:
            print("Transcription failed.")
            return
        
        # Save the transcript to a .txt file
        output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transcript)

        print(f"Transcription saved to: {output_file}")

    except Exception as e:
        print(f"Error in transcribe_single_file: {e}")
        print(f"File path: {os.path.abspath(input_file)}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Directory contents: {os.listdir(os.path.dirname(input_file))}")


def transcribe_all_files(input_dir, output_dir, model):
    # Check if directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: Directory not found: {input_dir}")
        return

    # Iterate through all files in the input directory
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        if file_name.lower().endswith(('.mp3', '.wav')):
            # Pass 'model' when calling transcribe_single_file
            transcribe_single_file(file_path, output_dir, model)  # Model is passed here


if __name__ == "__main__":
    # Load the user-selected Whisper model
    try:
        model = load_model()
        print(f"Whisper model loaded successfully: {model.device}")
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        sys.exit(1)
        
    # Prompt user for input type
    input_type = input("Do you want to transcribe a single file (S) or multiple files (M)? ").lower()

    if input_type == 's':
        input_file = strip_quotes(input("Enter the path to the audio file: "))
        output_dir = strip_quotes(input("Enter the directory to save the transcription: "))

        input_dir = os.path.dirname(input_file)
        print(f"Contents of {input_dir}:")
        for file in os.listdir(input_dir):
            print(f"  {file}")

    else:
        input_dir = strip_quotes(input("Enter the directory containing audio files: "))
        output_dir = strip_quotes(input("Enter the directory to save the transcriptions: "))

    # Ensure output directory exists
    try:
        os.makedirs(output_dir, exist_ok=True)
    except PermissionError:
        print(f"Error: Permission denied when trying to create or access {output_dir}")
        sys.exit(1)
    
    # Transcribe files based on user choice
    if input_type == 's':
        transcribe_single_file(input_file, output_dir, model)
    else:
        transcribe_all_files(input_dir, output_dir, model)