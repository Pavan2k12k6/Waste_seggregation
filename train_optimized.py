"""
Optimized Training Script with Best Hyperparameters
Uses lessons learned from initial training and tuning
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Fix for truncated/corrupted images - MUST BE BEFORE OTHER IMPORTS
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import sys
from pathlib import Path
import json
import numpy as np
from sklearn.utils.class_weight import compute_class_weight

sys.path.append(str(Path(__file__).parent / 'src'))

from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, callbacks
from data.data_collector import DataPreprocessor


def create_optimized_model(num_classes, input_shape=(224, 224, 3)):
    """
    Create optimized model with best hyperparameters
    Based on empirical results showing MobileNetV2 works well
    """
    
    # Load pre-trained MobileNetV2
    base_model = keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model initially
    base_model.trainable = False
    
    # Build optimized architecture with stronger regularization
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dropout(0.4),  # Increased dropout
        layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(0.002)),  # Stronger L2
        layers.BatchNormalization(),
        layers.Dropout(0.3),  # Increased dropout
        layers.Dense(128, activation='relu', kernel_regularizer=keras.regularizers.l2(0.002)),  # Stronger L2
        layers.BatchNormalization(),
        layers.Dropout(0.2),  # Added extra dropout layer
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model


def train_optimized_model():
    """Train model with optimized hyperparameters"""
    
    print("="*70)
    print("OPTIMIZED WASTE CLASSIFICATION MODEL TRAINING")
    print("="*70)
    print()
    
    # Configuration - Optimized for lower validation loss
    DATASET_PATH = 'dataset'
    MODEL_PATH = 'models/waste_classifier_optimized.h5'
    BATCH_SIZE = 16  # Smaller batch size for better generalization
    EPOCHS = 50  # More epochs with early stopping
    LEARNING_RATE = 0.0005  # Slightly higher learning rate
    IMAGE_SIZE = (224, 224)
    VALIDATION_SPLIT = 0.2
    
    print("Configuration:")
    print(f"  Dataset: {DATASET_PATH}")
    print(f"  Batch Size: {BATCH_SIZE}")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Learning Rate: {LEARNING_RATE}")
    print(f"  Image Size: {IMAGE_SIZE}")
    print(f"  Validation Split: {VALIDATION_SPLIT}")
    print()
    
    # Prepare data
    print("Preparing data...")
    preprocessor = DataPreprocessor(image_size=IMAGE_SIZE)
    train_gen, val_gen, class_indices = preprocessor.create_data_generator(
        dataset_path=DATASET_PATH,
        batch_size=BATCH_SIZE,
        validation_split=VALIDATION_SPLIT
    )
    
    class_names = list(class_indices.keys())
    num_classes = len(class_names)
    
    print(f"[OK] Data prepared")
    print(f"  Classes: {class_names}")
    print(f"  Number of classes: {num_classes}")
    print(f"  Training samples: {train_gen.samples}")
    print(f"  Validation samples: {val_gen.samples}")
    print()
    
    # Compute class weights for imbalanced data
    print("Computing class weights...")
    class_weights_array = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(train_gen.classes),
        y=train_gen.classes
    )
    class_weights = dict(enumerate(class_weights_array))
    
    print("[OK] Class weights computed:")
    for i, (class_name, weight) in enumerate(zip(class_names, class_weights_array)):
        print(f"  {class_name}: {weight:.3f}")
    print()
    
    # Create model
    print("Creating optimized model...")
    model = create_optimized_model(num_classes=num_classes, input_shape=(*IMAGE_SIZE, 3))
    
    # Compile model
    model.compile(
        optimizer=optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
    )
    
    print("[OK] Model created and compiled")
    print(f"  Total parameters: {model.count_params():,}")
    trainable_params = sum([keras.backend.count_params(w) for w in model.trainable_weights])
    print(f"  Trainable parameters: {trainable_params:,}")
    print()
    
    # Callbacks - Optimized for lower validation loss
    callbacks_list = [
        callbacks.EarlyStopping(
            monitor='val_loss',  # Monitor validation loss directly
            patience=12,  # More patience for better convergence
            restore_best_weights=True,
            verbose=1,
            mode='min'  # Minimize validation loss
        ),
        callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.3,  # More aggressive learning rate reduction
            patience=5,
            min_lr=1e-7,
            verbose=1,
            mode='min'
        ),
        callbacks.ModelCheckpoint(
            MODEL_PATH,
            monitor='val_loss',  # Save best model based on validation loss
            save_best_only=True,
            verbose=1,
            mode='min'
        ),
        callbacks.CSVLogger(
            'models/training_log.csv',
            append=False
        )
    ]
    
    # Train
    print("Starting training...")
    print("="*70)
    history = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=callbacks_list,
        class_weight=class_weights,
        verbose=1
    )
    
    # Evaluate
    print("\n" + "="*70)
    print("TRAINING COMPLETED - EVALUATING MODEL")
    print("="*70)
    
    val_loss, val_accuracy, val_top3_accuracy = model.evaluate(val_gen, verbose=0)
    
    print(f"\nFinal Results:")
    print(f"  Validation Accuracy: {val_accuracy*100:.2f}%")
    print(f"  Validation Top-3 Accuracy: {val_top3_accuracy*100:.2f}%")
    print(f"  Validation Loss: {val_loss:.4f}")
    print()
    
    # Save training history
    history_data = {
        'config': {
            'batch_size': BATCH_SIZE,
            'epochs': EPOCHS,
            'learning_rate': LEARNING_RATE,
            'image_size': IMAGE_SIZE,
            'validation_split': VALIDATION_SPLIT,
            'num_classes': num_classes,
            'class_names': class_names
        },
        'final_metrics': {
            'val_accuracy': float(val_accuracy),
            'val_top3_accuracy': float(val_top3_accuracy),
            'val_loss': float(val_loss)
        },
        'history': {
            'accuracy': [float(x) for x in history.history['accuracy']],
            'val_accuracy': [float(x) for x in history.history['val_accuracy']],
            'loss': [float(x) for x in history.history['loss']],
            'val_loss': [float(x) for x in history.history['val_loss']]
        }
    }
    
    with open('models/training_history.json', 'w') as f:
        json.dump(history_data, f, indent=2)
    
    print("[OK] Training history saved to: models/training_history.json")
    print("[OK] Model saved to: " + MODEL_PATH)
    print()
    
    # Copy to main model if better
    main_model_path = Path('models/waste_classifier.h5')
    if val_accuracy > 0.85:  # If accuracy is good
        import shutil
        shutil.copy(MODEL_PATH, main_model_path)
        print(f"[OK] Copied optimized model to: {main_model_path}")
        print()
    
    print("="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Evaluate model: python evaluate_model.py")
    print("2. Test with camera: python src/models/detect.py")
    print("3. Launch dashboard: python src/web/dashboard.py")
    print()
    
    return history, val_accuracy


if __name__ == "__main__":
    train_optimized_model()
