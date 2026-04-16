"""
Advanced Camera Evaluation with Detailed Metrics
Real-time waste classification with probability visualization
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
from datetime import datetime

# Configuration
MODEL_PATH = 'models/waste_classifier.h5'
CLASS_NAMES = ["e-waste", "glass", "metal", "organic", "paper", "plastic"]
IMAGE_SIZE = (224, 224)

# Colors for each class (BGR format)
CLASS_COLORS = {
    "e-waste": (0, 0, 255),      # Red
    "glass": (255, 191, 0),       # Deep Sky Blue
    "metal": (128, 128, 128),     # Gray
    "organic": (0, 255, 0),       # Green
    "paper": (255, 255, 255),     # White
    "plastic": (0, 165, 255)      # Orange
}

class WasteCameraEvaluator:
    def __init__(self, model_path=MODEL_PATH, camera_index=0):
        self.model_path = model_path
        self.camera_index = camera_index
        self.model = None
        self.cap = None
        self.stats = {
            'total_frames': 0,
            'predictions': {name: 0 for name in CLASS_NAMES},
            'start_time': None
        }
        
    def load_model(self):
        """Load the trained model"""
        if not Path(self.model_path).exists():
            print(f"[ERROR] Model not found at {self.model_path}")
            print("Please train the model first using: python train_optimized.py")
            return False
        
        print("[INFO] Loading model...")
        self.model = tf.keras.models.load_model(self.model_path)
        print("[OK] Model loaded successfully!")
        print(f"  - Input shape: {self.model.input_shape}")
        print(f"  - Output classes: {len(CLASS_NAMES)}")
        return True
    
    def initialize_camera(self):
        """Initialize camera"""
        print(f"[INFO] Opening camera {self.camera_index}...")
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print(f"[ERROR] Could not open camera {self.camera_index}")
            return False
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("[OK] Camera initialized successfully!")
        return True
    
    def preprocess_frame(self, frame):
        """Preprocess frame for model prediction"""
        img = cv2.resize(frame, IMAGE_SIZE)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        return img
    
    def draw_ui(self, frame, prediction, probabilities, fps):
        """Draw comprehensive UI on frame"""
        height, width = frame.shape[:2]
        
        # Create main info panel (left side)
        panel_width = 400
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (panel_width, height), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        y_offset = 30
        
        # Title
        cv2.putText(frame, "WASTE CLASSIFIER", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        y_offset += 40
        
        # Main prediction
        color = CLASS_COLORS.get(prediction, (255, 255, 255))
        cv2.putText(frame, f"{prediction.upper()}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        y_offset += 50
        
        # Confidence bar for main prediction
        main_conf = probabilities[CLASS_NAMES.index(prediction)]
        bar_width = int((panel_width - 20) * main_conf)
        cv2.rectangle(frame, (10, y_offset), (10 + bar_width, y_offset + 20), color, -1)
        cv2.rectangle(frame, (10, y_offset), (panel_width - 10, y_offset + 20), (255, 255, 255), 2)
        cv2.putText(frame, f"{main_conf*100:.1f}%", 
                   (panel_width - 80, y_offset + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 40
        
        # Separator
        cv2.line(frame, (10, y_offset), (panel_width - 10, y_offset), (255, 255, 255), 1)
        y_offset += 20
        
        # All class probabilities
        cv2.putText(frame, "All Probabilities:", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        y_offset += 25
        
        # Sort classes by probability
        sorted_indices = np.argsort(probabilities)[::-1]
        
        for idx in sorted_indices:
            class_name = CLASS_NAMES[idx]
            prob = probabilities[idx]
            color = CLASS_COLORS.get(class_name, (255, 255, 255))
            
            # Class name
            cv2.putText(frame, f"{class_name}:", 
                       (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Probability bar
            bar_w = int((panel_width - 120) * prob)
            cv2.rectangle(frame, (120, y_offset - 12), (120 + bar_w, y_offset - 2), color, -1)
            cv2.rectangle(frame, (120, y_offset - 12), (panel_width - 15, y_offset - 2), (150, 150, 150), 1)
            
            # Percentage
            cv2.putText(frame, f"{prob*100:.1f}%", 
                       (panel_width - 70, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            y_offset += 25
        
        # Statistics
        y_offset += 20
        cv2.line(frame, (10, y_offset), (panel_width - 10, y_offset), (255, 255, 255), 1)
        y_offset += 25
        
        cv2.putText(frame, "Statistics:", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        y_offset += 25
        
        cv2.putText(frame, f"FPS: {fps:.1f}", 
                   (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 20
        
        cv2.putText(frame, f"Frames: {self.stats['total_frames']}", 
                   (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 20
        
        elapsed = time.time() - self.stats['start_time']
        cv2.putText(frame, f"Time: {elapsed:.0f}s", 
                   (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Controls (bottom)
        y_offset = height - 80
        cv2.putText(frame, "Controls:", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y_offset += 20
        cv2.putText(frame, "S - Save image", 
                   (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        y_offset += 18
        cv2.putText(frame, "P - Pause/Resume", 
                   (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        y_offset += 18
        cv2.putText(frame, "Q/ESC - Quit", 
                   (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return frame
    
    def save_prediction(self, frame, prediction, confidence):
        """Save frame with prediction"""
        save_dir = Path('outputs/camera_predictions')
        save_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prediction}_{confidence*100:.0f}_{timestamp}.jpg"
        filepath = save_dir / filename
        
        cv2.imwrite(str(filepath), frame)
        print(f"[SAVED] {filepath}")
        return filepath
    
    def run(self):
        """Run the camera evaluation"""
        print("=" * 70)
        print("ADVANCED WASTE CLASSIFICATION - CAMERA EVALUATION")
        print("=" * 70)
        print()
        
        # Load model
        if not self.load_model():
            return
        
        # Initialize camera
        if not self.initialize_camera():
            return
        
        print()
        print("Starting evaluation...")
        print("=" * 70)
        
        # Initialize variables
        fps = 0
        frame_count = 0
        start_time = time.time()
        self.stats['start_time'] = start_time
        paused = False
        
        # Prediction smoothing
        prediction_history = []
        max_history = 5
        
        try:
            while True:
                if not paused:
                    ret, frame = self.cap.read()
                    if not ret:
                        print("[ERROR] Failed to read from camera")
                        break
                    
                    # Make prediction
                    preprocessed = self.preprocess_frame(frame)
                    predictions = self.model.predict(preprocessed, verbose=0)[0]
                    
                    # Get prediction
                    class_idx = np.argmax(predictions)
                    confidence = predictions[class_idx]
                    prediction = CLASS_NAMES[class_idx]
                    
                    # Update statistics
                    self.stats['total_frames'] += 1
                    self.stats['predictions'][prediction] += 1
                    
                    # Calculate FPS
                    frame_count += 1
                    if frame_count % 10 == 0:
                        elapsed = time.time() - start_time
                        fps = frame_count / elapsed
                    
                    # Draw UI
                    display_frame = self.draw_ui(frame.copy(), prediction, predictions, fps)
                else:
                    # Show paused message
                    cv2.putText(display_frame, "PAUSED", 
                               (display_frame.shape[1]//2 - 100, display_frame.shape[0]//2), 
                               cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                
                # Display frame
                cv2.imshow("Waste Classification - Advanced Evaluation", display_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:  # Q or ESC
                    print("\n[INFO] Quitting...")
                    break
                elif key == ord('s'):  # Save
                    self.save_prediction(frame, prediction, confidence)
                    # Show saved message
                    temp_frame = display_frame.copy()
                    cv2.putText(temp_frame, "SAVED!", 
                               (temp_frame.shape[1]//2 - 80, temp_frame.shape[0]//2), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    cv2.imshow("Waste Classification - Advanced Evaluation", temp_frame)
                    cv2.waitKey(500)
                elif key == ord('p'):  # Pause
                    paused = not paused
                    print(f"[INFO] {'Paused' if paused else 'Resumed'}")
        
        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup and show statistics"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
        # Print statistics
        print()
        print("=" * 70)
        print("EVALUATION SUMMARY")
        print("=" * 70)
        print(f"Total frames processed: {self.stats['total_frames']}")
        
        elapsed = time.time() - self.stats['start_time']
        print(f"Total time: {elapsed:.2f} seconds")
        print(f"Average FPS: {self.stats['total_frames'] / elapsed:.2f}")
        
        print("\nPrediction Distribution:")
        for class_name, count in sorted(self.stats['predictions'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.stats['total_frames'] * 100) if self.stats['total_frames'] > 0 else 0
            print(f"  {class_name:10s}: {count:5d} frames ({percentage:5.1f}%)")
        
        print("=" * 70)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced camera evaluation for waste classification')
    parser.add_argument('--camera', type=int, default=0, 
                       help='Camera index (default: 0)')
    parser.add_argument('--model', type=str, default=MODEL_PATH,
                       help='Path to model file')
    
    args = parser.parse_args()
    
    evaluator = WasteCameraEvaluator(model_path=args.model, camera_index=args.camera)
    evaluator.run()
