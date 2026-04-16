# Waste Classification AI System

Automated waste segregation system using deep learning for real-time classification.

## Features

- **6 Waste Categories**: Plastic, Metal, Paper, Glass, Organic, E-waste
- **High Accuracy**: 95%+ classification accuracy
- **Real-time Detection**: Camera-based waste identification
- **Web Dashboard**: Monitor and control system
- **Hardware Integration**: Automated sorting mechanism

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train Model (if needed)
```bash
python train_optimized.py
```

### 3. Evaluate Model
```bash
python evaluate_model.py
```

### 4. Run Real-time Detection
```bash
python src/models/detect.py --model_path models/waste_classifier.h5 --camera 0
```

### 5. Launch Web Dashboard
```bash
python src/web/dashboard.py --port 8080
```

## Project Structure

```
waste_segregation_ai/
├── dataset/              # Training data (6 categories)
├── src/                  # Source code
│   ├── data/            # Data handling
│   ├── models/          # Model implementation
│   ├── hardware/        # Hardware control
│   └── web/             # Web interface
├── models/              # Trained models
├── outputs/             # Results and reports
├── tests/               # Test suite
└── docs/                # Documentation
```

## Model Performance

- **Overall Accuracy**: 95%+
- **Training Time**: ~30-40 minutes
- **Inference Speed**: Real-time (30+ FPS)
- **Model Size**: ~9 MB (MobileNetV2)

## Key Scripts

- `train_optimized.py` - Train model with best hyperparameters
- `evaluate_model.py` - Comprehensive model evaluation
- `hyperparameter_tuning.py` - Optimize model parameters
- `demo.py` - Complete system demonstration
- `auto_cleanup.py` - Clean up project files

## Dataset

The model is trained on 7,472 images across 6 waste categories:
- E-waste: 190 images
- Glass: 511 images
- Metal: 680 images
- Organic: 4,722 images
- Paper: 870 images
- Plastic: 499 images

## Requirements

- Python 3.8+
- TensorFlow 2.x
- OpenCV
- NumPy
- scikit-learn
- matplotlib
- seaborn

## Documentation

- `ACCURACY_REPORT.md` - Detailed accuracy analysis
- `QUICK_SUMMARY.md` - Quick reference guide
- `docs/INSTALLATION.md` - Installation instructions
- `docs/USER_GUIDE.md` - User guide

## License

MIT License

## Contact

For issues or questions, please create a GitHub issue.
