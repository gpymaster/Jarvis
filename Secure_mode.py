import cv2
import mediapipe as mp
import time
import os
import subprocess

# Initialize Mediapipe Pose & Face Detection
mp_pose = mp.solutions.pose
mp_face_detection = mp.solutions.face_detection  # Face detection to reduce false positives
mp_drawing = mp.solutions.drawing_utils  # For visualization
pose = mp_pose.Pose()
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.6)  # Confidence threshold

# iMessage function
def send_imessage(contact_name, message):
    """Sends a normal iMessage text message."""
    script = f'''
    tell application "Messages"
        set targetBuddy to "+19252597318"
        set targetService to 1st service whose service type = iMessage
        send "{message}" to buddy targetBuddy of targetService
    end tell
    '''
    
    subprocess.run(["osascript", "-e", script])
    print(f"📩 iMessage sent with message: {message}")

# Person detection function
def detect_person():
    cap = cv2.VideoCapture(0)  # Open webcam
    
    cooldown_time = 30  # Seconds before sending another alert
    absence_threshold = 10  # Seconds to confirm no person
    frame_count_threshold = 5  # Require detection in 5 consecutive frames
    consecutive_detections = 0  # Counter for stable detection
    last_seen_time = 0
    last_sent_time = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to RGB for Mediapipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect pose and face
        pose_results = pose.process(rgb_frame)
        face_results = face_detection.process(rgb_frame)

        current_time = time.time()
        height, width, _ = frame.shape

        if pose_results.pose_landmarks:
            # Count the number of visible keypoints
            keypoint_count = sum(1 for lm in pose_results.pose_landmarks.landmark if lm.visibility > 0.5)

            # Calculate bounding box around detected person
            x_min, y_min, x_max, y_max = width, height, 0, 0
            for landmark in pose_results.pose_landmarks.landmark:
                x, y = int(landmark.x * width), int(landmark.y * height)
                x_min, y_min = min(x, x_min), min(y, y_min)
                x_max, y_max = max(x, x_max), max(y, y_max)

            # Expand bounding box for better framing
            padding = 20
            x_min, y_min = max(x_min - padding, 0), max(y_min - padding, 0)
            x_max, y_max = min(x_max + padding, width), min(y_max + padding, height)

            # Check for both pose and face detection
            if keypoint_count >= 6 and face_results.detections:
                consecutive_detections += 1
            else:
                consecutive_detections = 0  # Reset if not consistently detected

            if consecutive_detections < frame_count_threshold:
                print(f"⌛ Waiting for {frame_count_threshold - consecutive_detections} more frames...")
                continue  # Wait until detection is stable

            last_seen_time = current_time  # Reset absence timer

            if current_time - last_sent_time > cooldown_time:
                print("👤 Person detected!")

                # Draw bounding box around detected person
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 4)  # Red box

                # Save image with bounding box
                timestamp = int(current_time)
                filename = f"captured_frame_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 Frame saved as {filename}")

                # Send alert
                send_imessage('grayson', '⚠️Person Detected⚠️')
                subprocess.run(["open", filename])  # Opens the image on macOS
                exit()

        else:
            if current_time - last_seen_time > absence_threshold:
                print("🚫 No person detected")
                consecutive_detections = 0  # Reset detection count

        # Show webcam feed
        cv2.imshow('Webcam Feed', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_person()
