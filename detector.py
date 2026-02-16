import cv2
import numpy as np
import tensorflow as tf
import pickle
import mediapipe as mp
from collections import deque, Counter
import asyncio
import websockets
import json
import base64
import os


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("Se încarcă modelele combinate...")
try:
    model = tf.keras.models.load_model("model/combined_model.h5")
    with open("model/combined_label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)
    print("✅ Modelele au fost încărcate cu succes!")
except Exception as e:
    print(f"❌ Eroare la încărcarea modelelor: {e}")
    exit()


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


prediction_history = deque(maxlen=10)
confidence_threshold = 0.6


async def process_frame(websocket):
    print("🟢 Un client (frontend-ul JS) s-a conectat!")
    
    try:
        async for message in websocket:
            
            try:
                encoded_data = message.split(',')[1] 
                nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except Exception:
                continue

            if frame is None:
                continue

            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)
            
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    landmarks = []
                    for lm in hand_landmarks.landmark:
                        landmarks.extend([lm.x, lm.y, lm.z])
                    
                    if len(landmarks) == 63:
                        
                        pred = model.predict(np.array([landmarks]), verbose=0)[0]
                        pred_idx = np.argmax(pred)
                        confidence = pred[pred_idx]
                        
                        if confidence > confidence_threshold:
                            prediction = label_encoder.inverse_transform([pred_idx])[0]
                            prediction_history.append(prediction)
                            
                            
                            if len(prediction_history) == prediction_history.maxlen:
                                most_common = Counter(prediction_history).most_common(1)[0]
                                final_label = most_common[0]
                            else:
                                final_label = prediction
                            
                            
                            response = {
                                "status": "success",
                                "label": final_label,
                                "confidence": f"{confidence:.1%}"
                            }
                            await websocket.send(json.dumps(response))
                            break 

    except websockets.exceptions.ConnectionClosed:
        print("🔴 Clientul s-a deconectat.")
        prediction_history.clear() 
    except Exception as e:
        print(f"A aparut o eroare neașteptata: {e}")

#  Pornirea Serverului WebSocket 
async def main():
    print(" Pornesc serverul pe ws://localhost:8765 ...")
    async with websockets.serve(process_frame, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())