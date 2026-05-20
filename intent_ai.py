import requests
from google import genai
from elevenlabs import ElevenLabs
import pygame
import os
import json
import subprocess

# File to store the history
history_file = "history.json"

# Load history from file
def load_history():
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            return json.load(f)
    return []

def reset_history():
    with open(history_file, "w") as f:
        json.dump([], f)
    print("History has been reset.")

# Save history to file
def save_history(history):
    with open(history_file, "w") as f:
        json.dump(history, f)

# Initialize the history list
history = load_history()

def ask_ai(text, history):
    client = genai.Client(api_key="AIzaSyBbdvMY_qHmI8bULZcHiJTplnNmrfuVf8Y")
    # Combine history and current question
    prompt = "\n".join(history) + "\n" + text
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response.text

def speak_old(text_speach):
    if not text_speach:
        print("No text provided for speech synthesis.")
        return

    client = ElevenLabs(api_key="sk_fb4ff162b9c3e0c8bd2f345ae30fa096eab9378d300224f8")

    audio_generator = client.text_to_speech.convert(
        voice_id="ErXwobaYiN019PkySvjV",  # Adjust with your voice ID
        output_format="mp3_44100_128",  # Adjust format
        text=text_speach,
        model_id="eleven_multilingual_v2",  # Adjust model if needed
    )

    audio_data = b''.join(audio_generator)

    with open("output.mp3", "wb") as f:
        f.write(audio_data)
    pygame.mixer.init()
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


save_history(history)

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

# Example: Add a new function to test.py

# Replace this with your Wit.ai Server Access Token
WIT_ACCESS_TOKEN = "PBC23X5BGQFKMCVNV2YQVWNZT6NXWKLJ"
WIT_API_URL = "https://api.wit.ai/message?v=20230220&q="

# Function to get intent from Wit.ai
def get_intent(user_input):
    headers = {"Authorization": f"Bearer {WIT_ACCESS_TOKEN}"}
    response = requests.get(WIT_API_URL + user_input, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        intents = data.get("intents", [])

        if intents:
            return intents[0]["name"]  # Get the highest-confidence intent
        else:
            return "unknown"
    else:
        return "error"

# Function to handle intent actions
def handle_intent(intent):
    if intent == "wit$get_weather":
        return "It's sunny and 75°F outside."  # Replace with real weather API call
    elif intent == "wit$get_time":
        from datetime import datetime
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."
    elif intent == "joke":
        return "Why don't skeletons fight each other? Because they don't have the guts!"
    elif intent == "ask_ai":
        answer = ask_ai(user_input,history)
        print(answer)
 
    else:
        return "I don't understand that."




# Test the Wit.ai intents
user_input = input("Ask something: ")  # Example: "What is the weather?"
detected_intent = get_intent(user_input)

print(f"\nDetected Intent: {detected_intent}")
response = handle_intent(detected_intent)
print(f"Final Response: {response}")
