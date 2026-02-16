import cv2
import numpy as np
import tensorflow as tf
import pickle
import mediapipe as mp
from collections import deque

try:
    model = tf.keras.models.load_model("model/combined_model.h5")
    with open("model/combined_label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)
except:
    print("Error loading model.")
    exit()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

prediction_history = deque(maxlen=10)
confidence_threshold = 0.6

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    prediction_text = "No hand detected"
    confidence = 0
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            if len(landmarks) == 63:
                pred = model.predict(np.array([landmarks]), verbose=0)[0]
                pred_idx = np.argmax(pred)
                confidence = pred[pred_idx]
                
                if confidence > confidence_threshold:
                    prediction = label_encoder.inverse_transform([pred_idx])[0]
                    prediction_history.append(prediction)
                    if len(prediction_history) == prediction_history.maxlen:
                        from collections import Counter
                        most_common = Counter(prediction_history).most_common(1)[0]
                        prediction_text = f"{most_common[0]} ({confidence:.1%})"
                    else:
                        prediction_text = f"{prediction} ({confidence:.1%})"
                else:
                    prediction_text = f"Low confidence ({confidence:.1%})"
    
    h, w, _ = frame.shape
    
    cv2.putText(frame, prediction_text, (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
  
    
    cv2.imshow('Combined Sign Language Detection', frame)
    
    key = cv2.waitKey(1) & 0xFF
    

    if key == ord('t'):
        if confidence_threshold == 0.6:
            confidence_threshold = 0.7
        elif confidence_threshold == 0.7:
            confidence_threshold = 0.5
        else:
            confidence_threshold = 0.6
        print(f"Confidence threshold set to: {confidence_threshold}")
    
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
print("\nDetection stopped.")