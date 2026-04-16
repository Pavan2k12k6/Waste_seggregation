"""
Real-Time Camera Evaluation for Waste Classification
Test the model using live webcam feed
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import cv2
import numpy as np
import tensorflow as tf
from pathlib import Path
import time

# Configuration
MODEL_PATH = 'models/waste_classifier.h5'
CLASS_NAMES = ["e-waste", "glass", "metal", "organic", "paper", "plastic"]
IMAGE_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 0.5

# Colors for each class (BGR format)
CLASS_COLORS = {
    "e-waste": (0, 0, 255),      # Red
    "glass": (255, 191, 0),       # Deep Sky Blue
    "metal": (128, 128, 128),     # Gray
    "organic": (0, 255, 0),       # Green
    "paper": (255, 255, 255),     # White
    "plastic": (0, 165, 255)      # Orange
}

def load_model():
    """Load the trained model"""
    if not Path(MODEL_PATH).exists():
        print(f"[ERROR] Model not found at {MODEL_PATH}")
        print("Please train the model first using: python train_optimized.py")
        return None
    
    print("[INFO] Loading model...")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("[OK] Model loaded successfully!")
    return model

def preprocess_frame(frame):
    """Preprocess frame for model prediction"""
    # Resize frame
    img = cv2.resize(frame, IMAGE_SIZE)
    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Normalize
    img = img.astype(np.float32) / 255.0
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    return img

def draw_prediction_box(frame, prediction, confidence, fps):
    """Draw prediction information on frame"""
    height, width = frame.shape[:2]
    
    # Create semi-transparent overlay for info box
    overlay = frame.copy()
    box_height = 180
    cv2.rectangle(overlay, (0, 0), (width, box_height), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
    
    # Title
    cv2.putText(frame, "WASTE CLASSIFICATION - LIVE CAMERA", 
                (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Prediction
    color = CLASS_COLORS.get(prediction, (255, 255, 255))
    cv2.putText(frame, f"Detected: {prediction.upper()}", 
                (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
    
    # Confidence
    conf_color = (0, 255, 0) if confidence >= CONFIDENCE_THRESHOLD else (0, 165, 255)
    cv2.putText(frame, f"Confidence: {confidence*100:.1f}%", 
                (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, conf_color, 2)
    
    # FPS
    cv2.putText(frame, f"FPS: {fps:.1f}", 
                (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Instructions
    cv2.putText(frame, "Press 'S' to save | 'Q' to quit", 
                (width - 350, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Confidence bar
    bar_width = int((width - 40) * confidence)
    cv2.rectangle(frame, (20, height - 50), (20 + bar_width, height - 30), conf_color, -1)
    cv2.rectangle(frame, (20, height - 50), (width - 20, height - 30), (255, 255, 255), 2)
    
    return frame

def save_prediction(frame, prediction, confidence, save_dir='outputs/camera_predictions'):
    """Save frame with prediction"""
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{prediction}_{confidence*100:.0f}_{timestamp}.jpg"
    filepath = Path(save_dir) / filename
    cv2.imwrite(str(filepath), frame)
    print(f"[SAVED] {filepath}")
    return filepath

def run_camera_evaluation(camera_index=0):
    """Run real-time camera evaluation"""
    print("=" * 70)
    print("WASTE CLASSIFICATION - CAMERA EVALUATION")
    print("=" * 70)
    print()
    
    # Load model
    model = load_model()
    if model is None:
        return
    
    # Open camera
    print(f"[INFO] Opening camera {camera_index}...")
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"[ERROR] Could not open camera {camera_index}")
        print("Try changing camera_index (0, 1, 2, etc.)")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    print("[OK] Camera opened successfully!")
    print()
    print("Controls:")
    print("  - Press 'S' to save current prediction")
    print("  - Press 'Q' or ESC to quit")
    print("  - Press 'P' to pause/unpause")
    print()
    print("Starting evaluation...")
    print("=" * 70)
    
    # Variables for FPS calculation
    fps = 0
    frame_count = 0
    start_time = time.time()
    paused = False
    
    # Variables for prediction smoothing
    prediction_history = []
    max_history = 5
    
    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    print("[ERROR] Failed to read from camera")
                    break
                
                # Make prediction
                preprocessed = preprocess_frame(frame)
                predictions = model.predict(preprocessed, verbose=0)
                
                # Get prediction and confidence
                class_idx = np.argmax(predictions[0])
                confidence = predictions[0][class_idx]
                prediction = CLASS_NAMES[class_idx]
                
                # Smooth predictions
                prediction_history.append((prediction, confidence))
                if len(prediction_history) > max_history:
                    prediction_history.pop(0)
                
                # Use most common prediction
                if len(prediction_history) >= 3:
                    pred_counts = {}
                    for pred, conf in prediction_history:
                        pred_counts[pred] = pred_counts.get(pred, 0) + conf
                    prediction = max(pred_counts, key=pred_counts.get)
                    confidence = pred_counts[prediction] / len(prediction_history)
                
                # Calculate FPS
                frame_count += 1
                if frame_count % 10 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                
                # Draw prediction on frame
                display_frame = draw_prediction_box(frame.copy(), prediction, confidence, fps)
            else:
                # Show paused message
                cv2.putText(display_frame, "PAUSED", 
                           (display_frame.shape[1]//2 - 100, display_frame.shape[0]//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            
            # Display frame
            cv2.imshow("Waste Classification - Camera Evaluation", display_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # Q or ESC
                print("\n[INFO] Quitting...")
                break
            elif key == ord('s'):  # Save
                filepath = save_prediction(frame, prediction, confidence)
                # Show saved message
                temp_frame = display_frame.copy()
                cv2.putText(temp_frame, "SAVED!", 
                           (temp_frame.shape[1]//2 - 80, temp_frame.shape[0]//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                cv2.imshow("Waste Classification - Camera Evaluation", temp_frame)
                cv2.waitKey(500)
            elif key == ord('p'):  # Pause
                paused = not paused
                print(f"[INFO] {'Paused' if paused else 'Resumed'}")
    
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Print statistics
        print()
        print("=" * 70)
        print("EVALUATION SUMMARY")
        print("=" * 70)
        print(f"Total frames processed: {frame_count}")
        print(f"Average FPS: {fps:.2f}")
        print(f"Total time: {time.time() - start_time:.2f} seconds")
        print("=" * 70)

def test_camera_available():
    """Test if camera is available"""
    print("Testing camera availability...")
    for i in range(3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"[OK] Camera {i} is available")
            cap.release()
        else:
            print(f"[X] Camera {i} is not available")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time waste classification using camera')
    parser.add_argument('--camera', type=int, default=0, 
                       help='Camera index (default: 0)')
    parser.add_argument('--test', action='store_true',
                       help='Test camera availability')
    
    args = parser.parse_args()
    
    if args.test:
        test_camera_available()
    else:
        run_camera_evaluation(camera_index=args.camera)
