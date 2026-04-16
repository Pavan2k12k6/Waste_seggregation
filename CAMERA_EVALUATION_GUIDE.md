# Camera Evaluation Guide

## Overview
Real-time waste classification using your webcam to evaluate the trained model.

## Prerequisites
1. Trained model at `models/waste_classifier.h5`
2. Working webcam
3. Required packages: `opencv-python`, `tensorflow`, `numpy`

## Installation
```bash
pip install opencv-python tensorflow numpy pillow
```

## Available Scripts

### 1. Basic Camera Evaluation (`camera_evaluation.py`)
Simple real-time classification with clean interface.

**Features:**
- Real-time waste classification
- Confidence display with color-coded bars
- FPS counter
- Save predictions
- Prediction smoothing for stability

**Usage:**
```bash
# Navigate to the correct directory first
cd "c:\Users\pachu\Downloads\Waste Seggregation\Waste Seggregation"

# Run with default camera (camera 0)
python camera_evaluation.py

# Use different camera
python camera_evaluation.py --camera 1

# Test camera availability
python camera_evaluation.py --test
```

**Controls:**
- `S` - Save current frame with prediction
- `P` - Pause/Resume
- `Q` or `ESC` - Quit

### 2. Advanced Camera Evaluation (`camera_evaluation_advanced.py`)
Comprehensive evaluation with detailed metrics and probability visualization.

**Features:**
- All class probabilities displayed in real-time
- Sorted probability bars
- Detailed statistics (FPS, frame count, time)
- Prediction distribution tracking
- Professional UI with side panel

**Usage:**
```bash
# Navigate to the correct directory first
cd "c:\Users\pachu\Downloads\Waste Seggregation\Waste Seggregation"

# Run with default settings
python camera_evaluation_advanced.py

# Use different camera
python camera_evaluation_advanced.py --camera 1

# Use different model
python camera_evaluation_advanced.py --model models/waste_classifier_optimized.h5
```

**Controls:**
- `S` - Save current frame with prediction
- `P` - Pause/Resume
- `Q` or `ESC` - Quit

## Waste Categories
The model classifies waste into 6 categories:
1. **E-waste** (Red) - Electronic waste
2. **Glass** (Deep Sky Blue) - Glass items
3. **Metal** (Gray) - Metal objects
4. **Organic** (Green) - Organic/biodegradable waste
5. **Paper** (White) - Paper products
6. **Plastic** (Orange) - Plastic items

## Output
Saved predictions are stored in:
```
outputs/camera_predictions/
├── plastic_85_20241105_150230.jpg
├── paper_92_20241105_150245.jpg
└── ...
```

Filename format: `{category}_{confidence}_{timestamp}.jpg`

## Tips for Best Results

### 1. Lighting
- Use good lighting conditions
- Avoid shadows and glare
- Natural daylight works best

### 2. Camera Position
- Hold items 20-30 cm from camera
- Keep items centered in frame
- Avoid cluttered backgrounds

### 3. Item Presentation
- Show clear view of the item
- One item at a time for best accuracy
- Rotate item to show different angles

### 4. Performance
- Close other applications for better FPS
- Use USB 3.0 port for external cameras
- Lower resolution if FPS is too low

## Troubleshooting

### Camera Not Opening
```bash
# Test which cameras are available
python camera_evaluation.py --test

# Try different camera index
python camera_evaluation.py --camera 1
python camera_evaluation.py --camera 2
```

### Model Not Found
```bash
# Train the model first
python train_optimized.py

# Or specify model path
python camera_evaluation_advanced.py --model path/to/model.h5
```

### Low FPS
- Close other applications
- Reduce camera resolution
- Use a faster computer
- Ensure GPU support is enabled for TensorFlow

### Poor Predictions
- Ensure good lighting
- Clean camera lens
- Show items clearly
- Retrain model with more data

## Integration with Training

### Collect More Data
Use the camera to identify misclassifications and collect more training data:

1. Run camera evaluation
2. Save misclassified images (press `S`)
3. Move saved images to correct category in `dataset/`
4. Retrain the model

### Continuous Improvement Loop
```
1. Evaluate with camera → 2. Identify errors → 
3. Collect more data → 4. Retrain model → 
5. Evaluate again (repeat)
```

## Example Session

```bash
# 1. Navigate to project directory
cd "c:\Users\pachu\Downloads\Waste Seggregation\Waste Seggregation"

# 2. Run advanced evaluation
python camera_evaluation_advanced.py

# 3. Test different waste items
#    - Show plastic bottle → Should detect "plastic"
#    - Show paper → Should detect "paper"
#    - Show metal can → Should detect "metal"

# 4. Save interesting predictions (press S)

# 5. Review statistics when done (press Q)
```

## Performance Metrics

The evaluation will show:
- **Real-time FPS**: Frames processed per second
- **Confidence**: Model's certainty (0-100%)
- **All Probabilities**: Likelihood for each category
- **Prediction Distribution**: Which categories were detected most

## Next Steps

After camera evaluation:
1. Review saved predictions in `outputs/camera_predictions/`
2. Check `evaluate_model.py` for detailed accuracy metrics
3. Retrain if needed with additional data
4. Deploy to production environment

## Support

For issues or questions:
1. Check training logs in `models/training_log.csv`
2. Review model accuracy in `models/accuracy_report.json`
3. Ensure all dependencies are installed
4. Verify camera permissions in Windows settings
