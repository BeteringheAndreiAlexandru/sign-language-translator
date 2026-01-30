import cv2
import numpy as np
import mediapipe as mp
import os

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    os.makedirs(f"data/{letter}", exist_ok=True)

cap = cv2.VideoCapture(0)
recording = False
current_letter = ""
samples_collected = 0
target_samples = 200

print("Press A-Z to record 200 samples for that letter")
print("Press ESC to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    if results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
    
    if recording:
        cv2.putText(frame, f"Recording {current_letter}: {samples_collected}/{target_samples}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "Press A-Z to start recording", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Collect Data', frame)
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == 27:
        break
    
    if 97 <= key <= 122 and not recording: 
        current_letter = chr(key - 32) 
        recording = True
        samples_collected = 0
    
    if recording and results.multi_hand_landmarks:
        landmarks = []
        for lm in results.multi_hand_landmarks[0].landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        
        filename = f"data/{current_letter}/{current_letter}_{samples_collected:04d}.npy"
        np.save(filename, np.array(landmarks))
        samples_collected += 1
        
        if samples_collected >= target_samples:
            print(f"Finished {current_letter}")
            recording = False

cap.release()
cv2.destroyAllWindows()

print("Done")

