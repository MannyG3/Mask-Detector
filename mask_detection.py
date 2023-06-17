import datetime
import winsound

import cv2
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model

# Load face detection model
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Load mask detection model
model = load_model('mask_detection_model.h5')

# Initialize video capture
cap = cv2.VideoCapture(0)

# Set beep sound frequency and duration
freq = 2500
duration = 500  # milliseconds

while True:
    # Read video frame
    ret, frame = cap.read()

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Loop over each face and check for mask
    for (x, y, w, h) in faces:
        # Extract face ROI
        face_roi = frame[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (224, 224))

        # Preprocess face ROI for the mask detection model
        face_roi = preprocess_input(face_roi)

        # Make mask prediction
        prediction = model.predict(np.array([face_roi]))[0][0]

        # Calculate percentage of mask
        mask_percentage = round(prediction * 100)

        # Set label text and color based on mask prediction
        label = 'Mask: ' + str(mask_percentage) + '%' if prediction > 0.5 else 'No Mask: ' + str(100 - mask_percentage) + '%'
        color = (0, 255, 0) if label.startswith('Mask') else (0, 0, 255)

        # Draw bounding box and label text on the frame
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Play beep sound if no mask is detected
        if label.startswith('No Mask'):
            winsound.Beep(freq, duration)

        # Write timestamp on the frame
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(frame, timestamp, (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow('Face Mask Detection', frame)

    # Exit loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close all windows
cap.release()
cv2.destroyAllWindows()
