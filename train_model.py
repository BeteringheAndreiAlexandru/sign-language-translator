# train_simple_minimal.py
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow.keras import layers, models
import pickle

# 1. Load data
print("Loading data...")
X, y = [], []

for letter in os.listdir("data"):
    if os.path.isdir(f"data/{letter}"):
        for file in os.listdir(f"data/{letter}"):
            if file.endswith('.npy'):
                landmarks = np.load(f"data/{letter}/{file}")
                X.append(landmarks)
                y.append(letter)

X = np.array(X)
y = np.array(y)

# 2. Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# 3. Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")
print(f"Classes: {len(label_encoder.classes_)}")

# 4. Create simple model
model = models.Sequential([
    layers.Dense(128, activation='relu', input_shape=(X.shape[1],)),
    layers.Dropout(0.3),
    layers.Dense(64, activation='relu'),
    layers.Dense(len(label_encoder.classes_), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 5. Train model
print("\nTraining model...")
model.fit(X_train, y_train, 
          validation_data=(X_test, y_test),
          epochs=20,
          batch_size=32,
          verbose=1)

# 6. Save model
os.makedirs("model", exist_ok=True)
model.save("model/simple_model.h5")

with open("model/label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

# 7. Evaluate
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
print(f"\nTest accuracy: {test_acc:.2%}")
print("Model saved to 'model/simple_model.h5'")