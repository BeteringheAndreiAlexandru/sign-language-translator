import cv2
import numpy as np
import mediapipe as mp
import os

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    os.makedirs(f"data/{letter}", exist_ok=True)

words = ["thankyou", "food", "candy", "yes", "no", "please"]
for word in words:
    os.makedirs(f"data/{word}", exist_ok=True)

cap = cv2.VideoCapture(0)
recording = False
current_class = ""
samples_collected = 0
target_samples = 200

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    hand_detected = results.multi_hand_landmarks is not None
    
    if hand_detected:
        mp_drawing.draw_landmarks(frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
    
    if recording:
        cv2.putText(frame, f"Recording {current_class}: {samples_collected}/{target_samples}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        if not hand_detected:
            cv2.putText(frame, "Show hand!", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "Press A-Z or 1-6 to start", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Data Collection', frame)
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == 27:
        break
    
    if not recording:
        if 97 <= key <= 122:
            current_class = chr(key - 32).upper()
            recording = True
            samples_collected = 0
        elif 49 <= key <= 54:
            word_index = key - 49
            current_class = words[word_index]
            recording = True
            samples_collected = 0
    
    if recording and hand_detected:
        landmarks = []
        for lm in results.multi_hand_landmarks[0].landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        
        class_dir = f"data/{current_class}"
        existing = len([f for f in os.listdir(class_dir) if f.endswith('.npy')])
        filename = f"{class_dir}/{current_class}_{existing:04d}.npy"
        np.save(filename, np.array(landmarks))
        
        samples_collected += 1

        if samples_collected >= target_samples:
            total = len([f for f in os.listdir(class_dir) if f.endswith('.npy')])
            recording = False

cap.release()
cv2.destroyAllWindows()
print("\nData collection complete!")