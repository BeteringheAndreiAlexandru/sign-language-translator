# detect_simple_minimal.py
import cv2
import numpy as np
import tensorflow as tf
import pickle
import mediapipe as mp

# Load model
model = tf.keras.models.load_model("model/simple_model.h5")
with open("model/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# Setup MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# Start camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    prediction = "No hand"
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Extract landmarks
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            
            # Predict
            if len(landmarks) == 63:
                pred = model.predict(np.array([landmarks]), verbose=0)
                pred_idx = np.argmax(pred)
                confidence = np.max(pred)
                
                if confidence > 0.7:
                    prediction = f"{label_encoder.inverse_transform([pred_idx])[0]} ({confidence:.1%})"
            
            # Draw landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    # Show prediction
    cv2.putText(frame, prediction, (10, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Sign Language Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()