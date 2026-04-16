import tensorflow as tf
import numpy as np
import cv2
import os

# Path to trained model
MODEL_PATH = os.path.join("models", "waste_classifier.h5")

# Load the trained model
print("[INFO] Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("[INFO] Model loaded successfully!")

# Define your class labels (adjust these to match your dataset)
CLASS_NAMES = ["e-waste", "glass", "metal", "organic", "paper", "plastic"]

# Image preprocessing function
def preprocess_image(image_path, target_size=(224, 224)):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, target_size)
    image = image / 255.0  # normalize
    return np.expand_dims(image, axis=0)

# Detection function
def detect_waste(image_path):
    image = preprocess_image(image_path)
    predictions = model.predict(image)
    class_idx = np.argmax(predictions)
    confidence = float(np.max(predictions))
    
    print(f"\n[RESULT] Predicted class: {CLASS_NAMES[class_idx]}")
    print(f"[CONFIDENCE] {confidence * 100:.2f}%")

    return CLASS_NAMES[class_idx], confidence

if __name__ == "__main__":
    # Example: single image prediction
    test_image = input("Enter the path to an image: ").strip()
    detect_waste(test_image)
