import tkinter as tk
from tkinter import filedialog

def select_audio_file():
    """
    Opens a file dialog for selecting an audio file.
    
    Returns:
        str: Path to selected audio file, or None if canceled
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title='Select Audio File',
        filetypes=[
            ('Audio Files', '*.mp3 *.wav *.m4a *.flac'),
            ('All Files', '*.*')
        ]
    )
    return file_path if file_path else None
