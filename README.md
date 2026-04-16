# Automated Waste Segregation AI Project

An end-to-end AI system for automatic waste classification and segregation using computer vision and machine learning.

## Features

- Real-time waste classification from camera feed
- Support for 6 waste categories: Plastic, Metal, Paper, Glass, Organic, E-waste
- Automated sorting via servo motors/robotic arms
- Web dashboard for monitoring
- Hardware integration with Raspberry Pi

## Project Structure

```
waste_segregation_ai/
├── dataset/                 # Training data organized by category
├── models/                  # Saved model files
├── src/
│   ├── data/               # Data collection and preprocessing
│   ├── models/             # Model training and inference
│   ├── hardware/           # Hardware control and integration
│   ├── web/                # Web dashboard
│   └── utils/              # Utility functions
├── tests/                  # Test files
├── docs/                   # Documentation
└── deployment/             # Deployment scripts
```

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up dataset in the `dataset/` directory
4. Train the model: `python src/models/train.py`
5. Run real-time detection: `python src/models/detect.py`

## Hardware Requirements

- Camera (USB webcam or Raspberry Pi camera)
- Raspberry Pi 4 (recommended)
- Servo motors or robotic arm
- Sorting bins
- Optional: Conveyor belt system

## Usage

### Training
```bash
python src/models/train.py --data_path dataset/ --epochs 50
```

### Real-time Detection
```bash
python src/models/detect.py --model_path models/waste_classifier.h5
```

### Hardware Integration
```bash
python src/hardware/sorting_controller.py
```

## License

MIT License
