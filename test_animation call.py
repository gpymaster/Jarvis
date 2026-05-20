import threading
import os
import subprocess
import time
import edge_tts
import pygame
import asyncio

# Global variable to store the process
process = None

def start_java():
    global process
    file_path = '/Users/graysonkeenan/IdeaProjects/jarvis gui/src/Main.java'
    os.chdir(os.path.dirname(file_path))

    subprocess.run(["javac", "Main.java"])
    process = subprocess.Popen(["java", "Main"])

    print('Java process started')
    return process

def stop_java():
    global process
    if process is not None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        process = None
        print("Java process stopped")
    else:
        print("No Java process running")



async def async_speak(text):
    # Start Java animation in a thread
    start_thread = threading.Thread(target=start_java)
    start_thread.start()

    # Generate audio
    tts = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await tts.save("output.mp3")

    print('Audio saved as output.mp3')

    # Give Java a moment to load
    time.sleep(0.5)

    # Start audio playback
    pygame.mixer.init()
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()

    # Wait for audio to finish
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Stop Java animation in a thread
    stop_thread = threading.Thread(target=stop_java)
    stop_thread.start()

def speak(text):
    asyncio.run(async_speak(text))



speak('how are you today sir where is the pudding')