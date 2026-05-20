import cv2
import face_recognition
import numpy as np
import os

# Load the saved face encoding
def recognize_face():
    if os.path.exists("my_face.npy"):
        my_face_encoding = np.load("my_face.npy")
        print("Face encoding loaded successfully!")
    else:
        print("No saved face encoding found. Run `save_face.py` first.")
        exit()

    # Open webcam
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        print("Error: Could not access the camera.")
        exit()

    # Set high resolution
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            # Compare detected face with saved encoding
            matches = face_recognition.compare_faces([my_face_encoding], face_encoding)
            
            if matches[0]:
                name = "You"
                color = (0, 255, 0)  # Green for recognized face
               
            else:
                name = "Unknown"
                color = (0, 0, 255)  # Red for unknown face
                

            # Draw rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # Show frame
        cv2.imshow('Face Recognition (HD)', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    video_capture.release()
    cv2.destroyAllWindows()

recognize_face()