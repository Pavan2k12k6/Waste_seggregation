"""
Hyperparameter Tuning for Waste Classification Model
Optimizes model parameters for best accuracy
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sys
from pathlib import Path
import json
import numpy as np
from datetime import datetime
from sklearn.utils.class_weight import compute_class_weight

sys.path.append(str(Path(__file__).parent / 'src'))

from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, callbacks
from data.data_collector import DataPreprocessor


class HyperparameterTuner:
    """Hyperparameter tuning for waste classification"""
    
    def __init__(self, dataset_path='dataset'):
        self.dataset_path = dataset_path
        self.results = []
        
    def create_optimized_model(self, num_classes, input_shape, 
                               base_model_name='MobileNetV2',
                               dense_units=256, dropout_rate=0.3,
                               learning_rate=0.0001):
        """Create optimized model with given hyperparameters"""
        
        # Load base model
        if base_model_name == 'MobileNetV2':
            base_model = keras.applications.MobileNetV2(
                input_shape=input_shape,
                include_top=False,
                weights='imagenet'
            )
        elif base_model_name == 'ResNet50':
            base_model = keras.applications.ResNet50(
                input_shape=input_shape,
                include_top=False,
                weights='imagenet'
            )
        elif base_model_name == 'EfficientNetB0':
            base_model = keras.applications.EfficientNetB0(
                input_shape=input_shape,
                include_top=False,
                weights='imagenet'
            )
        else:
            raise ValueError(f"Unsupported model: {base_model_name}")
        
        base_model.trainable = False
        
        # Build model
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.BatchNormalization(),
            layers.Dropout(dropout_rate),
            layers.Dense(dense_units, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(dropout_rate * 0.7),
            layers.Dense(dense_units // 2, activation='relu'),
            layers.Dropout(dropout_rate * 0.5),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        # Compile
        model.compile(
            optimizer=optimizers.Adam(learning_rate=learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3)]
        )
        
        return model
    
    def train_with_config(self, config, train_gen, val_gen, class_weights):
        """Train model with specific configuration"""
        
        print(f"\n{'='*70}")
        print(f"Testing Configuration:")
        print(f"  Base Model: {config['base_model']}")
        print(f"  Dense Units: {config['dense_units']}")
        print(f"  Dropout: {config['dropout_rate']}")
        print(f"  Learning Rate: {config['learning_rate']}")
        print(f"  Batch Size: {config['batch_size']}")
        print(f"{'='*70}\n")
        
        # Create model
        model = self.create_optimized_model(
            num_classes=train_gen.num_classes,
            input_shape=(224, 224, 3),
            base_model_name=config['base_model'],
            dense_units=config['dense_units'],
            dropout_rate=config['dropout_rate'],
            learning_rate=config['learning_rate']
        )
        
        # Callbacks
        model_path = f"models/tuned_{config['base_model']}_{config['dense_units']}.h5"
        callbacks_list = [
            callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=8,
                restore_best_weights=True,
                verbose=1
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=4,
                min_lr=1e-7,
                verbose=1
            ),
            callbacks.ModelCheckpoint(
                model_path,
                monitor='val_accuracy',
                save_best_only=True,
                verbose=0
            )
        ]
        
        # Train
        history = model.fit(
            train_gen,
            epochs=config['epochs'],
            validation_data=val_gen,
            callbacks=callbacks_list,
            class_weight=class_weights,
            verbose=1
        )
        
        # Get best results
        best_val_acc = max(history.history['val_accuracy'])
        best_train_acc = max(history.history['accuracy'])
        
        result = {
            'config': config,
            'best_val_accuracy': float(best_val_acc),
            'best_train_accuracy': float(best_train_acc),
            'model_path': model_path,
            'history': {
                'val_accuracy': [float(x) for x in history.history['val_accuracy']],
                'accuracy': [float(x) for x in history.history['accuracy']],
                'val_loss': [float(x) for x in history.history['val_loss']],
                'loss': [float(x) for x in history.history['loss']]
            }
        }
        
        self.results.append(result)
        
        print(f"\n[RESULT] Best Validation Accuracy: {best_val_acc*100:.2f}%")
        print(f"[RESULT] Best Training Accuracy: {best_train_acc*100:.2f}%\n")
        
        return result
    
    def run_tuning(self):
        """Run hyperparameter tuning"""
        
        print("="*70)
        print("HYPERPARAMETER TUNING FOR WASTE CLASSIFICATION")
        print("="*70)
        print()
        
        # Prepare data
        print("Preparing data...")
        preprocessor = DataPreprocessor(image_size=(224, 224))
        
        # Test different batch sizes
        configs_to_test = [
            # Configuration 1: MobileNetV2 - Balanced
            {
                'base_model': 'MobileNetV2',
                'dense_units': 256,
                'dropout_rate': 0.3,
                'learning_rate': 0.0001,
                'batch_size': 32,
                'epochs': 25
            },
            # Configuration 2: MobileNetV2 - Higher capacity
            {
                'base_model': 'MobileNetV2',
                'dense_units': 512,
                'dropout_rate': 0.4,
                'learning_rate': 0.0001,
                'batch_size': 32,
                'epochs': 25
            },
            # Configuration 3: MobileNetV2 - Lower learning rate
            {
                'base_model': 'MobileNetV2',
                'dense_units': 256,
                'dropout_rate': 0.3,
                'learning_rate': 0.00005,
                'batch_size': 32,
                'epochs': 25
            },
            # Configuration 4: EfficientNetB0 - Best architecture
            {
                'base_model': 'EfficientNetB0',
                'dense_units': 256,
                'dropout_rate': 0.3,
                'learning_rate': 0.0001,
                'batch_size': 32,
                'epochs': 25
            }
        ]
        
        best_result = None
        best_accuracy = 0
        
        for i, config in enumerate(configs_to_test, 1):
            print(f"\n{'#'*70}")
            print(f"# Configuration {i}/{len(configs_to_test)}")
            print(f"{'#'*70}\n")
            
            # Create data generators with current batch size
            train_gen, val_gen, class_indices = preprocessor.create_data_generator(
                dataset_path=self.dataset_path,
                batch_size=config['batch_size'],
                validation_split=0.2
            )
            
            # Compute class weights
            class_weights_array = compute_class_weight(
                class_weight='balanced',
                classes=np.unique(train_gen.classes),
                y=train_gen.classes
            )
            class_weights = dict(enumerate(class_weights_array))
            
            # Train with this configuration
            result = self.train_with_config(config, train_gen, val_gen, class_weights)
            
            # Track best
            if result['best_val_accuracy'] > best_accuracy:
                best_accuracy = result['best_val_accuracy']
                best_result = result
        
        # Save results
        results_file = 'models/hyperparameter_tuning_results.json'
        with open(results_file, 'w') as f:
            json.dump({
                'all_results': self.results,
                'best_config': best_result['config'],
                'best_accuracy': best_result['best_val_accuracy'],
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        print("\n" + "="*70)
        print("HYPERPARAMETER TUNING COMPLETED")
        print("="*70)
        print(f"\nBest Configuration:")
        print(f"  Base Model: {best_result['config']['base_model']}")
        print(f"  Dense Units: {best_result['config']['dense_units']}")
        print(f"  Dropout Rate: {best_result['config']['dropout_rate']}")
        print(f"  Learning Rate: {best_result['config']['learning_rate']}")
        print(f"  Batch Size: {best_result['config']['batch_size']}")
        print(f"\nBest Validation Accuracy: {best_result['best_val_accuracy']*100:.2f}%")
        print(f"Model saved to: {best_result['model_path']}")
        print(f"\nAll results saved to: {results_file}")
        print()
        
        return best_result


def main():
    """Main function"""
    tuner = HyperparameterTuner(dataset_path='dataset')
    best_result = tuner.run_tuning()
    
    print("="*70)
    print("NEXT STEPS")
    print("="*70)
    print(f"1. Evaluate best model: python evaluate_model.py")
    print(f"2. Copy best model: copy {best_result['model_path']} models/waste_classifier.h5")
    print(f"3. Test with camera: python src/models/detect.py")
    print()


if __name__ == "__main__":
    main()
