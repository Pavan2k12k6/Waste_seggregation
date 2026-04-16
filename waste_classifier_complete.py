"""
Complete Waste Classification System
Combines camera evaluation, image detection, and model testing
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
import sys

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

class WasteClassifier:
    def __init__(self, model_path=MODEL_PATH):
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        if not Path(self.model_path).exists():
            print(f"[ERROR] Model not found at {self.model_path}")
            print("Please train the model first using: python train_optimized.py")
            return False
        
        print("[INFO] Loading model...")
        self.model = tf.keras.models.load_model(self.model_path)
        print("[OK] Model loaded successfully!")
        return True
    
    def preprocess_image(self, image):
        """Preprocess image for prediction"""
        if isinstance(image, str) or isinstance(image, Path):
            # Load from file
            img = cv2.imread(str(image))
            if img is None:
                raise ValueError(f"Could not load image from {image}")
        else:
            # Already a numpy array (from camera)
            img = image
        
        # Resize and normalize
        img = cv2.resize(img, IMAGE_SIZE)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        return img
    
    def predict(self, image):
        """Predict waste category"""
        if self.model is None:
            print("[ERROR] Model not loaded")
            return None, None, None
        
        preprocessed = self.preprocess_image(image)
        predictions = self.model.predict(preprocessed, verbose=0)[0]
        
        class_idx = np.argmax(predictions)
        confidence = predictions[class_idx]
        prediction = CLASS_NAMES[class_idx]
        
        return prediction, confidence, predictions
    
    def predict_from_file(self, image_path):
        """Predict from image file"""
        print(f"\n[INFO] Processing: {image_path}")
        
        prediction, confidence, all_probs = self.predict(image_path)
        
        if prediction:
            print(f"\n{'='*60}")
            print(f"[RESULT] Predicted class: {prediction.upper()}")
            print(f"[CONFIDENCE] {confidence*100:.2f}%")
            print(f"{'='*60}")
            
            print("\nAll Probabilities:")
            sorted_indices = np.argsort(all_probs)[::-1]
            for idx in sorted_indices:
                class_name = CLASS_NAMES[idx]
                prob = all_probs[idx]
                bar = '█' * int(prob * 50)
                print(f"  {class_name:10s}: {prob*100:5.2f}% {bar}")
            print()
        
        return prediction, confidence, all_probs
    
    def run_camera_evaluation(self, camera_index=0):
        """Run real-time camera evaluation"""
        print("\n" + "="*70)
        print("CAMERA EVALUATION MODE")
        print("="*70)
        
        # Open camera
        print(f"[INFO] Opening camera {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"[ERROR] Could not open camera {camera_index}")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("[OK] Camera opened!")
        print("\nControls:")
        print("  S - Save prediction")
        print("  P - Pause/Resume")
        print("  Q/ESC - Quit")
        print("="*70 + "\n")
        
        fps = 0
        frame_count = 0
        start_time = time.time()
        paused = False
        stats = {name: 0 for name in CLASS_NAMES}
        
        try:
            while True:
                if not paused:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Predict
                    prediction, confidence, all_probs = self.predict(frame)
                    
                    if prediction:
                        stats[prediction] += 1
                    
                    # Calculate FPS
                    frame_count += 1
                    if frame_count % 10 == 0:
                        fps = frame_count / (time.time() - start_time)
                    
                    # Draw UI
                    display_frame = self.draw_camera_ui(frame.copy(), prediction, 
                                                        confidence, all_probs, fps, stats)
                else:
                    cv2.putText(display_frame, "PAUSED", 
                               (display_frame.shape[1]//2 - 100, display_frame.shape[0]//2), 
                               cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                
                cv2.imshow("Waste Classification - Camera", display_frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:
                    break
                elif key == ord('s'):
                    self.save_prediction(frame, prediction, confidence)
                    temp = display_frame.copy()
                    cv2.putText(temp, "SAVED!", 
                               (temp.shape[1]//2 - 80, temp.shape[0]//2), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    cv2.imshow("Waste Classification - Camera", temp)
                    cv2.waitKey(500)
                elif key == ord('p'):
                    paused = not paused
        
        except KeyboardInterrupt:
            pass
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.print_camera_stats(stats, frame_count, time.time() - start_time)
    
    def draw_camera_ui(self, frame, prediction, confidence, all_probs, fps, stats):
        """Draw UI on camera frame"""
        height, width = frame.shape[:2]
        
        # Info panel
        panel_width = 400
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (panel_width, height), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        y = 30
        
        # Title
        cv2.putText(frame, "WASTE CLASSIFIER", 
                   (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        y += 50
        
        # Main prediction
        if prediction:
            color = CLASS_COLORS.get(prediction, (255, 255, 255))
            cv2.putText(frame, f"{prediction.upper()}", 
                       (10, y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            y += 40
            
            # Confidence bar
            bar_width = int((panel_width - 20) * confidence)
            cv2.rectangle(frame, (10, y), (10 + bar_width, y + 20), color, -1)
            cv2.rectangle(frame, (10, y), (panel_width - 10, y + 20), (255, 255, 255), 2)
            cv2.putText(frame, f"{confidence*100:.1f}%", 
                       (panel_width - 80, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y += 40
        
        # Separator
        cv2.line(frame, (10, y), (panel_width - 10, y), (255, 255, 255), 1)
        y += 20
        
        # All probabilities
        cv2.putText(frame, "Probabilities:", 
                   (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        y += 25
        
        if all_probs is not None:
            sorted_indices = np.argsort(all_probs)[::-1]
            for idx in sorted_indices:
                class_name = CLASS_NAMES[idx]
                prob = all_probs[idx]
                color = CLASS_COLORS.get(class_name, (255, 255, 255))
                
                cv2.putText(frame, f"{class_name}:", 
                           (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
                bar_w = int((panel_width - 120) * prob)
                cv2.rectangle(frame, (120, y - 12), (120 + bar_w, y - 2), color, -1)
                cv2.rectangle(frame, (120, y - 12), (panel_width - 15, y - 2), (150, 150, 150), 1)
                
                cv2.putText(frame, f"{prob*100:.1f}%", 
                           (panel_width - 70, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                y += 25
        
        # Stats
        y += 20
        cv2.line(frame, (10, y), (panel_width - 10, y), (255, 255, 255), 1)
        y += 25
        
        cv2.putText(frame, f"FPS: {fps:.1f}", 
                   (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Controls
        y = height - 80
        cv2.putText(frame, "Controls:", 
                   (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y += 20
        cv2.putText(frame, "S - Save | P - Pause", 
                   (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        y += 18
        cv2.putText(frame, "Q/ESC - Quit", 
                   (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return frame
    
    def save_prediction(self, frame, prediction, confidence):
        """Save prediction"""
        save_dir = Path('outputs/predictions')
        save_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prediction}_{confidence*100:.0f}_{timestamp}.jpg"
        filepath = save_dir / filename
        
        cv2.imwrite(str(filepath), frame)
        print(f"[SAVED] {filepath}")
    
    def print_camera_stats(self, stats, frames, elapsed):
        """Print camera statistics"""
        print("\n" + "="*70)
        print("CAMERA EVALUATION SUMMARY")
        print("="*70)
        print(f"Total frames: {frames}")
        print(f"Total time: {elapsed:.2f}s")
        print(f"Average FPS: {frames/elapsed:.2f}")
        print("\nDetection Distribution:")
        for class_name, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / frames * 100) if frames > 0 else 0
            print(f"  {class_name:10s}: {count:5d} ({percentage:5.1f}%)")
        print("="*70)

def main_menu():
    """Main menu for the application"""
    print("\n" + "="*70)
    print(" "*20 + "WASTE CLASSIFICATION SYSTEM")
    print("="*70)
    print("\n1. Classify from Image File")
    print("2. Real-time Camera Classification")
    print("3. Batch Process Multiple Images")
    print("4. Test Camera Availability")
    print("5. Exit")
    print("\n" + "="*70)
    
    choice = input("\nEnter your choice (1-5): ").strip()
    return choice

def test_camera():
    """Test camera availability"""
    print("\n" + "="*70)
    print("TESTING CAMERA AVAILABILITY")
    print("="*70)
    for i in range(3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"[OK] Camera {i} is available")
            cap.release()
        else:
            print(f"[X] Camera {i} is not available")
    print("="*70)

def batch_process(classifier):
    """Batch process multiple images"""
    print("\n" + "="*70)
    print("BATCH PROCESSING MODE")
    print("="*70)
    
    folder = input("\nEnter folder path (or press Enter for current directory): ").strip()
    if not folder:
        folder = "."
    
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"[ERROR] Folder not found: {folder}")
        return
    
    # Find all images
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    images = []
    for ext in image_extensions:
        images.extend(folder_path.glob(f"*{ext}"))
        images.extend(folder_path.glob(f"*{ext.upper()}"))
    
    if not images:
        print("[ERROR] No images found in folder")
        return
    
    print(f"\n[INFO] Found {len(images)} images")
    print("Processing...\n")
    
    results = []
    for img_path in images:
        try:
            prediction, confidence, _ = classifier.predict_from_file(str(img_path))
            results.append({
                'file': img_path.name,
                'prediction': prediction,
                'confidence': confidence
            })
        except Exception as e:
            print(f"[ERROR] Failed to process {img_path.name}: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("BATCH PROCESSING SUMMARY")
    print("="*70)
    print(f"{'File':<30} {'Prediction':<15} {'Confidence':<10}")
    print("-"*70)
    for result in results:
        print(f"{result['file']:<30} {result['prediction']:<15} {result['confidence']*100:>8.2f}%")
    print("="*70)

def main():
    """Main application"""
    print("\n" + "="*70)
    print(" "*15 + "WASTE CLASSIFICATION SYSTEM")
    print(" "*20 + "Complete Solution")
    print("="*70)
    
    # Initialize classifier
    classifier = WasteClassifier()
    
    if classifier.model is None:
        print("\n[ERROR] Cannot proceed without model")
        return
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            # Image file classification
            image_path = input("\nEnter image path: ").strip().strip('"').strip("'")
            if image_path:
                try:
                    classifier.predict_from_file(image_path)
                except Exception as e:
                    print(f"[ERROR] {e}")
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            # Camera classification
            camera_idx = input("\nEnter camera index (default 0): ").strip()
            camera_idx = int(camera_idx) if camera_idx else 0
            classifier.run_camera_evaluation(camera_index=camera_idx)
        
        elif choice == '3':
            # Batch processing
            batch_process(classifier)
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            # Test camera
            test_camera()
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            # Exit
            print("\nThank you for using Waste Classification System!")
            break
        
        else:
            print("\n[ERROR] Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Application terminated by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
