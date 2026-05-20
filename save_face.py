
import face_recognition
import numpy as np
import cv2

# Open webcam
video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("Error: Could not access the camera.")
    exit()

print("Look at the camera. Capturing face...")

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Convert to RGB format
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect face in the frame
    face_locations = face_recognition.face_locations(rgb_frame)

    if face_locations:
        # Encode the first detected face
        face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]

        # Save encoding to a file
        np.save("my_face.npy", face_encoding)
        print("Face encoding saved successfully!")
        break

# Cleanup
video_capture.release()
cv2.destroyAllWindows()
