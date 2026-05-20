"""
Person Detection System
Detects when a person is in front of the screen using webcam
"""

import cv2
from datetime import datetime

class PersonDetector:
    def __init__(self):
        """Initialize the person detector with Haar Cascade classifier"""
        # Load pre-trained models for face and body detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')

        # Initialize video capture (0 for default webcam)
        self.cap = cv2.VideoCapture(0)

        # Detection settings
        self.person_detected = False
        self.detection_callback = None

    def set_callback(self, callback_function):
        """Set a callback function to be called when person is detected/not detected"""
        self.detection_callback = callback_function

    def detect_person(self, frame):
        """
        Detect if a person is in the frame
        Returns: (person_found, faces, bodies)
        """
        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # Detect bodies
        bodies = self.body_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(50, 50)
        )

        # Person detected if either face or body found
        person_found = len(faces) > 0 or len(bodies) > 0

        return person_found, faces, bodies

    def draw_detections(self, frame, faces, bodies):
        """Draw rectangles around detected faces and bodies"""
        # Draw rectangles around faces (green)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, 'Face', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Draw rectangles around bodies (blue)
        for (x, y, w, h) in bodies:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, 'Body', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        return frame

    def run(self, show_window=True, verbose=True):
        """
        Run the person detection loop

        Args:
            show_window: Whether to display the video window
            verbose: Whether to print detection status
        """
        print("Starting person detection...")
        print("Press 'q' to quit")

        try:
            while True:
                # Capture frame-by-frame
                ret, frame = self.cap.read()

                if not ret:
                    print("Failed to grab frame")
                    break

                # Detect person
                person_found, faces, bodies = self.detect_person(frame)

                # Check for state change
                if person_found != self.person_detected:
                    self.person_detected = person_found
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if person_found:
                        if verbose:
                            print(f"[{timestamp}] PERSON DETECTED!")
                        if self.detection_callback:
                            self.detection_callback(True)
                    else:
                        if verbose:
                            print(f"[{timestamp}] Person left the screen")
                        if self.detection_callback:
                            self.detection_callback(False)

                if show_window:
                    # Draw detections
                    frame = self.draw_detections(frame, faces, bodies)

                    # Add status text
                    status = "PERSON DETECTED" if person_found else "No person detected"
                    color = (0, 255, 0) if person_found else (0, 0, 255)
                    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

                    # Display the frame
                    cv2.imshow('Person Detection', frame)

                # Break loop on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("\nStopping detection...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Release resources"""
        self.cap.release()
        cv2.destroyAllWindows()
        print("Person detection stopped")


# Example callback function
def on_person_detected(detected):
    """Example callback that gets called when detection state changes"""
    if detected:
        print(">>> Callback: Person is present!")
        # Add your custom actions here (e.g., wake screen, start recording, etc.)
    else:
        print(">>> Callback: Person left!")
        # Add your custom actions here (e.g., lock screen, pause recording, etc.)


if __name__ == "__main__":
    # Create detector instance
    detector = PersonDetector()

    # Optional: Set a callback function
    detector.set_callback(on_person_detected)

    # Run the detector
    detector.run(show_window=True, verbose=True)



