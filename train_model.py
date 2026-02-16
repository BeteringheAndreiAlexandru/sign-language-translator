import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow.keras import layers, models
import pickle

X, y = [], []

all_classes = sorted([d for d in os.listdir("data") if os.path.isdir(f"data/{d}")])

for class_name in all_classes:
    class_dir = f"data/{class_name}"
    if os.path.isdir(class_dir):
        for file in os.listdir(class_dir):
            if file.endswith('.npy'):
                landmarks = np.load(os.path.join(class_dir, file))
                X.append(landmarks)
                y.append(class_name)

X = np.array(X)
y = np.array(y)

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

model = models.Sequential([
    layers.Dense(256, activation='relu', input_shape=(X.shape[1],)),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    
    layers.Dense(128, activation='relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.2),
    
    layers.Dense(len(label_encoder.classes_), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)
model.summary()

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy',
        patience=15,
        restore_best_weights=True,
        verbose=1
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        verbose=1
    )
]

print("\nTraining model...")
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=50,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)

os.makedirs("model", exist_ok=True)
model.save("model/combined_model.h5")

with open("model/combined_label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

train_loss, train_acc = model.evaluate(X_train, y_train, verbose=0)
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)


np.save('model/training_history.npy', history.history)

sample_indices = np.random.choice(len(X_test), 10, replace=False)
for idx in sample_indices:
    sample = X_test[idx].reshape(1, -1)
    true_label = label_encoder.inverse_transform([y_test[idx]])[0]
    pred = model.predict(sample, verbose=0)
    pred_label = label_encoder.inverse_transform([np.argmax(pred)])[0]
    confidence = np.max(pred)