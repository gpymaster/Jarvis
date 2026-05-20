import os
import subprocess

def create_new_file(file_path, content=""):
    try:
        with open(file_path, 'x') as file:
            file.write(content)
        print(f"File created at: {file_path}")
        # Open the file in Visual Studio Code
        subprocess.run(["code", file_path])
    except FileExistsError:
        print(f"File already exists at: {file_path}")
        # Open the existing file in Visual Studio Code
        subprocess.run(["code", file_path])

def open_code_file(file_path):
    """Opens a specific file in VS Code."""
    subprocess.run(["code", file_path], check=True)

def overwrite_file(file_path, content):
    """Overwrites the file with new content."""
    with open(file_path, "w") as f:
        f.write(content)


def append_to_file(file_path, content):
    """Appends content to an existing file."""
    with open(file_path, "a") as f:
        f.write("\n" + content)  # Adds a newline before appending


google_ai = 'google_ai.py'
test = 'test.html'
face_recongnition = 'face_recongnition.py'
siri_protype = 'siri_protype.py'
playlist = 'playlist.py'

rock_papper_siccos_game = 'rock_papper_siccos_game.py'
AI_coder = 'AI_coder.py'

my_face = 'my_face.npy'
new_speech = 'new_speech.py'


append_to_file(google_ai, 'print(' ')')
print()