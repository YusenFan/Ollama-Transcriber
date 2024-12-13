import argparse
from pydub import AudioSegment
import os
import subprocess
import sys

def check_ffmpeg():
    """
    Verify FFmpeg installation on Windows.
    Checks both system PATH and current directory.
    """
    try:
        # Check if ffmpeg exists in PATH
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE,
                      check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        # Check current directory
        if os.path.exists('ffmpeg.exe'):
            return True
        print("FFmpeg not found. Please ensure ffmpeg.exe is:\n"
              "1. Added to system PATH, or\n"
              "2. Placed in the same directory as this script\n"
              "Download FFmpeg from: https://github.com/BtbN/FFmpeg-Builds/releases")
        return False

def get_supported_formats():
    """
    Returns a list of commonly supported audio formats.
    """
    return ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac', 'wma']

def validate_format(format_str):
    """
    Validates if the provided format is supported.
    
    format_str: Format to validate
    
    True if format is supported, False otherwise
    """
    return format_str.lower() in get_supported_formats()

def convert_audio(input_file, output_format, output_file=None):
    """
    Convert audio file to specified format using pydub.
        input_file: Path to input audio file
        output_format: Desired output format
        output_file: Path for output file
    """
    try:
        # Check FFmpeg availability
        if not check_ffmpeg():
            return False

        # Validate input file
        if not os.path.isfile(input_file):
            print(f"Error: Input file not found: {input_file}")
            return False

        # Validate output format
        if not validate_format(output_format):
            print(f"Error: Unsupported output format: {output_format}")
            print(f"Supported formats: {', '.join(get_supported_formats())}")
            return False

        # Get original filename without extension
        original_filename = os.path.splitext(os.path.basename(input_file))[0]

        # Handle output path
        if not output_file:
            # If no output specified, save in same directory as input
            output_file = f"{original_filename}.{output_format}"
        elif os.path.isdir(output_file):
            # If output is a directory, use original filename in that directory
            output_file = os.path.join(output_file, f"{original_filename}.{output_format}")
        else:
            # If specific output path given, ensure it has the correct extension
            output_dir = os.path.dirname(output_file)
            if output_dir:
                output_file = os.path.join(output_dir, f"{original_filename}.{output_format}")
            
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir:
            try:
                os.makedirs(output_dir, exist_ok=True)
                print(f"Created/verified directory: {output_dir}")
            except Exception as e:
                print(f"Error creating directory {output_dir}: {str(e)}")
                return False

        '''# Debug information (optional sanity check in the event that tool doesn't work)
        print(f"Debug Info:")
        print(f"Input file: {input_file}")
        print(f"Output format: {output_format}")
        print(f"Output file: {output_file}")
        print(f"Output directory exists: {os.path.exists(output_dir)}")
        print(f"Current working directory: {os.getcwd()}")
        '''

        # Load and convert audio
        try:
            print(f"Loading {input_file}...")
            audio = AudioSegment.from_file(input_file)
            
            print(f"Converting to {output_format}...")
            audio.export(output_file, format=output_format)
            
            print(f"Successfully saved to: {output_file}")
            return True

        except Exception as e:
            print(f"Conversion error: {str(e)}")
            print(f"Full error details: {type(e).__name__}")
            return False

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

def main():
    """
    Main function to handle command-line arguments and conversion process.
    """
    parser = argparse.ArgumentParser(
        description="Audio Format Converter for Windows",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input audio file"
    )
    parser.add_argument(
        "--output_format",
        required=True,
        help=f"Output format. Supported: {', '.join(get_supported_formats())}"
    )
    parser.add_argument(
        "--output",
        help="Output file path (optional)"
    )

    # Handle Windows-style paths
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    
    # Convert backslashes to forward slashes for consistency
    input_file = args.input.replace('\\', '/')
    output_file = args.output.replace('\\', '/') if args.output else None
    
    success = convert_audio(input_file, args.output_format, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
    