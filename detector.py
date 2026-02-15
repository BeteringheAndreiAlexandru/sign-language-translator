import cv2
import numpy as np
import mediapipe as mp
import pickle
import asyncio
import websockets
import json
import base64
import os


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow.keras.models import load_model


print("Se încarcă modelele din folderul 'model'...")

try:
    
    with open("model/label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)

    model = load_model("model/simple_model.h5")

    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1)

    print("✅ Modelele au fost încărcate cu succes!")

except FileNotFoundError as e:
    print(f"❌ Eroare: Nu am putut găsi fișierul. Asigură-te că există folderul 'model' și fișierele în el. Detalii: {e}")
    exit()
except Exception as e:
    print(f"❌ A apărut o eroare la încărcarea modelelor: {e}")
    exit()


async def process_frame(websocket):
    print("🟢 Un client (frontend-ul JS) s-a conectat!")
    
    try:
        async for message in websocket:
            # Decodarea imaginii primite 
            try:
                encoded_data = message.split(',')[1] 
                nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except Exception as e:
                print(f"Eroare la decodarea imaginii: {e}")
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
                        pred = model.predict(np.array([landmarks]), verbose=0)
                        
                        pred_idx = np.argmax(pred)
                        confidence = np.max(pred)
                        
                        if confidence > 0.7:
                            label = label_encoder.inverse_transform([pred_idx])[0]
                            
                            response = {
                                "status": "success",
                                "label": label,
                                "confidence": f"{confidence:.1%}"
                            }
                            
                            
                            await websocket.send(json.dumps(response))
                            break 

    except websockets.exceptions.ConnectionClosed:
        print("🔴 Clientul s-a deconectat.")
    except Exception as e:
        print(f"A aparut o eroare: {e}")

# --- 3. Pornirea Serverului WebSocket ---
async def main():
    print("🚀 Pornesc serverul pe ws://localhost:8765 ...")
    # Pornim serverul care ascultă pe portul 8765
    async with websockets.serve(process_frame, "localhost", 8765):
        await asyncio.Future()  # Menținem serverul pornit la nesfârșit

if __name__ == "__main__":
    asyncio.run(main())