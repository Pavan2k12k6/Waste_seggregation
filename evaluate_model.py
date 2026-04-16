"""
Model Accuracy Evaluation Script
Evaluates the trained waste classification model and generates detailed accuracy report
"""

import os
import sys
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from tensorflow import keras
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import precision_recall_fscore_support
from data.data_collector import DataPreprocessor


def evaluate_model_accuracy(model_path='models/waste_classifier.h5', 
                            dataset_path='dataset',
                            batch_size=32,
                            image_size=(224, 224)):
    """
    Comprehensive model accuracy evaluation
    """
    print("=" * 70)
    print("WASTE CLASSIFICATION MODEL - ACCURACY EVALUATION")
    print("=" * 70)
    print()
    
    # Check if model exists
    if not Path(model_path).exists():
        print(f"[X] ERROR: Model not found at {model_path}")
        print(f"   Please train the model first using: python src/models/train.py")
        return None
    
    # Check if dataset exists
    if not Path(dataset_path).exists():
        print(f"[X] ERROR: Dataset not found at {dataset_path}")
        print(f"   Please prepare the dataset first")
        return None
    
    print(f"[OK] Model path: {model_path}")
    print(f"[OK] Dataset path: {dataset_path}")
    print()
    
    try:
        # Load model
        print("Loading model...")
        model = keras.models.load_model(model_path)
        print(f"[OK] Model loaded successfully")
        print(f"  - Input shape: {model.input_shape}")
        print(f"  - Output shape: {model.output_shape}")
        print(f"  - Total parameters: {model.count_params():,}")
        print()
        
        # Prepare data
        print("Preparing test data...")
        preprocessor = DataPreprocessor(image_size=image_size)
        
        # Create test data generator (using validation split as test set)
        train_gen, test_gen, class_indices = preprocessor.create_data_generator(
            dataset_path=dataset_path,
            batch_size=batch_size,
            validation_split=0.2
        )
        
        class_names = list(class_indices.keys())
        # Filter out metadata directory if present
        if 'metadata' in class_names:
            class_names.remove('metadata')
            print("[WARNING] Removed 'metadata' from class names - it's not a valid waste category")
        
        num_classes = len(class_names)
        
        print(f"[OK] Test data prepared")
        print(f"  - Number of classes: {num_classes}")
        print(f"  - Class names: {class_names}")
        print(f"  - Test samples: {test_gen.samples}")
        print()
        
        # Evaluate model
        print("Evaluating model on test set...")
        print("-" * 70)
        
        # Get predictions
        predictions = model.predict(test_gen, verbose=1)
        predicted_classes = np.argmax(predictions, axis=1)
        true_classes = test_gen.classes
        
        # Calculate overall accuracy
        overall_accuracy = accuracy_score(true_classes, predicted_classes)
        
        print()
        print("=" * 70)
        print("OVERALL ACCURACY RESULTS")
        print("=" * 70)
        print(f"Overall Accuracy: {overall_accuracy * 100:.2f}%")
        print()
        
        # Per-class metrics
        precision, recall, f1, support = precision_recall_fscore_support(
            true_classes, predicted_classes, average=None, zero_division=0
        )
        
        print("=" * 70)
        print("PER-CLASS ACCURACY METRICS")
        print("=" * 70)
        print(f"{'Class':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<10}")
        print("-" * 70)
        
        for i, class_name in enumerate(class_names):
            print(f"{class_name:<15} {precision[i]*100:>10.2f}%  {recall[i]*100:>10.2f}%  "
                  f"{f1[i]*100:>10.2f}%  {support[i]:>8}")
        
        print("-" * 70)
        avg_precision = np.mean(precision)
        avg_recall = np.mean(recall)
        avg_f1 = np.mean(f1)
        print(f"{'Average':<15} {avg_precision*100:>10.2f}%  {avg_recall*100:>10.2f}%  "
              f"{avg_f1*100:>10.2f}%  {sum(support):>8}")
        print()
        
        # Detailed classification report
        print("=" * 70)
        print("DETAILED CLASSIFICATION REPORT")
        print("=" * 70)
        report = classification_report(true_classes, predicted_classes, 
                                      target_names=class_names, zero_division=0)
        print(report)
        
        # Confusion matrix
        print("=" * 70)
        print("CONFUSION MATRIX")
        print("=" * 70)
        cm = confusion_matrix(true_classes, predicted_classes)
        
        # Plot confusion matrix
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=class_names, yticklabels=class_names,
                   cbar_kws={'label': 'Count'})
        plt.title(f'Confusion Matrix - Overall Accuracy: {overall_accuracy*100:.2f}%', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Predicted Class', fontsize=12)
        plt.ylabel('True Class', fontsize=12)
        plt.tight_layout()
        
        cm_path = 'models/confusion_matrix_evaluation.png'
        plt.savefig(cm_path, dpi=300, bbox_inches='tight')
        print(f"[OK] Confusion matrix saved to: {cm_path}")
        plt.close()
        
        # Per-class accuracy bar chart
        plt.figure(figsize=(14, 6))
        x = np.arange(len(class_names))
        width = 0.25
        
        plt.bar(x - width, precision * 100, width, label='Precision', alpha=0.8)
        plt.bar(x, recall * 100, width, label='Recall', alpha=0.8)
        plt.bar(x + width, f1 * 100, width, label='F1-Score', alpha=0.8)
        
        plt.xlabel('Waste Category', fontsize=12)
        plt.ylabel('Score (%)', fontsize=12)
        plt.title(f'Per-Class Performance Metrics - Overall Accuracy: {overall_accuracy*100:.2f}%',
                 fontsize=14, fontweight='bold')
        plt.xticks(x, class_names, rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        metrics_path = 'models/per_class_metrics.png'
        plt.savefig(metrics_path, dpi=300, bbox_inches='tight')
        print(f"[OK] Per-class metrics chart saved to: {metrics_path}")
        plt.close()
        
        # Create comprehensive report
        report_data = {
            'overall_metrics': {
                'accuracy': float(overall_accuracy),
                'average_precision': float(avg_precision),
                'average_recall': float(avg_recall),
                'average_f1_score': float(avg_f1)
            },
            'per_class_metrics': {},
            'model_info': {
                'model_path': model_path,
                'input_shape': str(model.input_shape),
                'output_shape': str(model.output_shape),
                'total_parameters': int(model.count_params()),
                'num_classes': num_classes,
                'class_names': class_names
            },
            'test_info': {
                'test_samples': int(test_gen.samples),
                'batch_size': batch_size,
                'image_size': image_size
            }
        }
        
        for i, class_name in enumerate(class_names):
            report_data['per_class_metrics'][class_name] = {
                'precision': float(precision[i]),
                'recall': float(recall[i]),
                'f1_score': float(f1[i]),
                'support': int(support[i]),
                'accuracy_percentage': float(precision[i] * 100)
            }
        
        # Save report
        report_path = 'models/accuracy_report.json'
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"[OK] Detailed accuracy report saved to: {report_path}")
        print()
        
        # Summary
        print("=" * 70)
        print("EVALUATION SUMMARY")
        print("=" * 70)
        print(f"[OK] Overall Model Accuracy: {overall_accuracy * 100:.2f}%")
        print(f"[OK] Average Precision: {avg_precision * 100:.2f}%")
        print(f"[OK] Average Recall: {avg_recall * 100:.2f}%")
        print(f"[OK] Average F1-Score: {avg_f1 * 100:.2f}%")
        print()
        
        # Identify best and worst performing classes
        best_class_idx = np.argmax(f1)
        worst_class_idx = np.argmin(f1)
        
        print(f"Best performing class: {class_names[best_class_idx]} (F1: {f1[best_class_idx]*100:.2f}%)")
        print(f"Worst performing class: {class_names[worst_class_idx]} (F1: {f1[worst_class_idx]*100:.2f}%)")
        print()
        
        # Check if accuracy is acceptable
        if overall_accuracy >= 0.90:
            print("[EXCELLENT] Model accuracy is above 90%")
        elif overall_accuracy >= 0.80:
            print("[GOOD] Model accuracy is above 80%")
        elif overall_accuracy >= 0.70:
            print("[FAIR] Model accuracy is above 70% but could be improved")
        else:
            print("[POOR] Model accuracy is below 70% - retraining recommended")
        
        print()
        print("=" * 70)
        
        return report_data
        
    except Exception as e:
        print(f"[X] ERROR during evaluation: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def check_for_errors():
    """
    Check for common errors in the project
    """
    print("\n" + "=" * 70)
    print("CHECKING FOR COMMON ERRORS")
    print("=" * 70)
    print()
    
    errors_found = []
    warnings_found = []
    
    # Check 1: Model file exists
    if not Path('models/waste_classifier.h5').exists():
        errors_found.append("Model file not found - Please train the model first")
    else:
        print("[OK] Model file exists")
    
    # Check 2: Dataset exists
    if not Path('dataset').exists():
        errors_found.append("Dataset directory not found")
    else:
        print("[OK] Dataset directory exists")
        
        # Check for class directories
        expected_classes = ['plastic', 'metal', 'paper', 'glass', 'organic', 'e-waste', 'cardboard']
        found_classes = [d.name for d in Path('dataset').iterdir() if d.is_dir()]
        
        if len(found_classes) == 0:
            errors_found.append("No class directories found in dataset")
        else:
            print(f"[OK] Found {len(found_classes)} class directories: {found_classes}")
            
            # Check if each class has images
            for class_dir in found_classes:
                class_path = Path('dataset') / class_dir
                images = list(class_path.glob('*.jpg')) + list(class_path.glob('*.png'))
                if len(images) == 0:
                    warnings_found.append(f"No images found in {class_dir} directory")
                else:
                    print(f"  - {class_dir}: {len(images)} images")
    
    # Check 3: Required Python packages
    print("\n[OK] Checking required packages...")
    required_packages = {
        'tensorflow': 'tensorflow',
        'numpy': 'numpy',
        'opencv-python': 'cv2',
        'matplotlib': 'matplotlib',
        'scikit-learn': 'sklearn',
        'seaborn': 'seaborn'
    }
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"  [OK] {package_name}")
        except ImportError:
            errors_found.append(f"Required package '{package_name}' not installed")
    
    print()
    
    # Report errors and warnings
    if errors_found:
        print("[X] ERRORS FOUND:")
        for i, error in enumerate(errors_found, 1):
            print(f"  {i}. {error}")
        print()
    
    if warnings_found:
        print("[!] WARNINGS:")
        for i, warning in enumerate(warnings_found, 1):
            print(f"  {i}. {warning}")
        print()
    
    if not errors_found and not warnings_found:
        print("[OK] No errors or warnings found!")
        print()
    
    return len(errors_found) == 0


if __name__ == "__main__":
    # Check for errors first
    no_errors = check_for_errors()
    
    if no_errors:
        # Evaluate model accuracy
        print("\nStarting model accuracy evaluation...\n")
        result = evaluate_model_accuracy()
        
        if result:
            print("\n[OK] Evaluation completed successfully!")
            print(f"   Check 'models/accuracy_report.json' for detailed results")
            print(f"   Check 'models/confusion_matrix_evaluation.png' for confusion matrix")
            print(f"   Check 'models/per_class_metrics.png' for per-class metrics")
    else:
        print("\n[X] Please fix the errors above before evaluating the model")
