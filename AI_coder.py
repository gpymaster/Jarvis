import time
import os
import subprocess


def mac_lert(seconds):
    print(f"Timer set for {seconds} seconds...")
    time.sleep(seconds)
    
    # Display macOS alert dialog
    os.system('osascript -e \'tell app "System Events" to display dialog "Time is up!"\'')
    subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"])
# Example: Set a 10-second timer


def countdown(minutes):
    seconds = minutes * 60
    for remaining in range(seconds, 0, -1):
        print(f"Time left: {remaining // 60}m {remaining % 60}s", end="\r")
        time.sleep(1)
    
    print("\nTime is up!")  
    mac_lert

countdown(1)


# Example: 10-second countdown, 5 seconds of continuous alarm sound


