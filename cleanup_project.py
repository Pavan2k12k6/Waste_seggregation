"""
Project Cleanup Script
Removes unnecessary files and organizes the project
"""

import os
import shutil
from pathlib import Path
import json


def cleanup_project():
    """Clean up unnecessary files and organize project"""
    
    print("="*70)
    print("PROJECT CLEANUP")
    print("="*70)
    print()
    
    files_to_remove = []
    dirs_to_remove = []
    files_removed = 0
    space_saved = 0
    
    # 1. Remove temporary image files (captured frames and classifications)
    print("1. Cleaning temporary image files...")
    temp_patterns = [
        'captured_frame_*.jpg',
        'frame_*.jpg',
        'classification_*.jpg',
        'classification_*.json'
    ]
    
    for pattern in temp_patterns:
        for file in Path('.').glob(pattern):
            size = file.stat().st_size
            files_to_remove.append((str(file), size))
            print(f"   - {file.name} ({size/1024:.1f} KB)")
    
    # 2. Remove old/redundant documentation
    print("\n2. Cleaning redundant documentation...")
    redundant_docs = [
        'demo_simple.py',  # Keep only main demo.py
        'train_improved.py',  # Replaced by hyperparameter_tuning.py
        'fix_dataset_and_retrain.py',  # One-time use, no longer needed
    ]
    
    for doc in redundant_docs:
        if Path(doc).exists():
            size = Path(doc).stat().st_size
            files_to_remove.append((doc, size))
            print(f"   - {doc} ({size/1024:.1f} KB)")
    
    # 3. Clean up old model files (keep only the best one)
    print("\n3. Checking model files...")
    models_dir = Path('models')
    if models_dir.exists():
        model_files = list(models_dir.glob('*.h5'))
        if len(model_files) > 1:
            print(f"   Found {len(model_files)} model files")
            print(f"   Keeping: waste_classifier.h5 (main model)")
            for model_file in model_files:
                if model_file.name != 'waste_classifier.h5':
                    size = model_file.stat().st_size
                    print(f"   - {model_file.name} ({size/1024/1024:.1f} MB) - will be removed")
                    # Don't auto-remove models, let user decide
    
    # 4. Clean up __pycache__ directories
    print("\n4. Cleaning Python cache files...")
    for pycache in Path('.').rglob('__pycache__'):
        dirs_to_remove.append(str(pycache))
        print(f"   - {pycache}")
    
    # 5. Summary
    print("\n" + "="*70)
    print("CLEANUP SUMMARY")
    print("="*70)
    print(f"\nFiles to remove: {len(files_to_remove)}")
    total_size = sum(size for _, size in files_to_remove)
    print(f"Space to be freed: {total_size/1024/1024:.2f} MB")
    print(f"\nDirectories to remove: {len(dirs_to_remove)}")
    
    # Ask for confirmation
    print("\n" + "="*70)
    response = input("Do you want to proceed with cleanup? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print("\nCleaning up...")
        
        # Remove files
        for file_path, size in files_to_remove:
            try:
                os.remove(file_path)
                files_removed += 1
                space_saved += size
                print(f"   [OK] Removed: {file_path}")
            except Exception as e:
                print(f"   [X] Failed to remove {file_path}: {e}")
        
        # Remove directories
        for dir_path in dirs_to_remove:
            try:
                shutil.rmtree(dir_path)
                print(f"   [OK] Removed: {dir_path}")
            except Exception as e:
                print(f"   [X] Failed to remove {dir_path}: {e}")
        
        print(f"\n[OK] Cleanup completed!")
        print(f"   Files removed: {files_removed}")
        print(f"   Space freed: {space_saved/1024/1024:.2f} MB")
    else:
        print("\n[!] Cleanup cancelled")
    
    print()


def organize_project():
    """Organize project structure"""
    
    print("="*70)
    print("PROJECT ORGANIZATION")
    print("="*70)
    print()
    
    # Create organized structure
    dirs_to_create = [
        'outputs/classifications',  # For classification results
        'outputs/frames',  # For captured frames
        'outputs/reports',  # For evaluation reports
        'outputs/plots',  # For training plots
    ]
    
    print("Creating organized directory structure...")
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   [OK] {dir_path}")
    
    # Move files to organized locations
    print("\nOrganizing files...")
    
    # Move classification results
    for file in Path('.').glob('classification_*.jpg'):
        dest = Path('outputs/classifications') / file.name
        if not dest.exists():
            shutil.move(str(file), str(dest))
            print(f"   Moved: {file.name} -> outputs/classifications/")
    
    for file in Path('.').glob('classification_*.json'):
        dest = Path('outputs/classifications') / file.name
        if not dest.exists():
            shutil.move(str(file), str(dest))
    
    # Move captured frames
    for file in Path('.').glob('frame_*.jpg'):
        dest = Path('outputs/frames') / file.name
        if not dest.exists():
            shutil.move(str(file), str(dest))
            print(f"   Moved: {file.name} -> outputs/frames/")
    
    for file in Path('.').glob('captured_frame_*.jpg'):
        dest = Path('outputs/frames') / file.name
        if not dest.exists():
            shutil.move(str(file), str(dest))
    
    # Move reports
    models_dir = Path('models')
    if models_dir.exists():
        for file in models_dir.glob('*.json'):
            dest = Path('outputs/reports') / file.name
            if not dest.exists():
                shutil.copy(str(file), str(dest))
                print(f"   Copied: {file.name} -> outputs/reports/")
        
        for file in models_dir.glob('*.png'):
            dest = Path('outputs/plots') / file.name
            if not dest.exists():
                shutil.copy(str(file), str(dest))
                print(f"   Copied: {file.name} -> outputs/plots/")
    
    print("\n[OK] Project organized!")
    print()


def create_clean_structure_doc():
    """Create documentation for clean project structure"""
    
    structure = """# Clean Project Structure

## Directory Organization

```
waste_segregation_ai/
├── dataset/                    # Training data (6 categories)
│   ├── e-waste/
│   ├── glass/
│   ├── metal/
│   ├── organic/
│   ├── paper/
│   └── plastic/
│
├── src/                        # Source code
│   ├── data/                   # Data handling
│   │   ├── data_collector.py
│   │   └── download_datasets.py
│   ├── models/                 # Model implementation
│   │   ├── waste_classifier.py
│   │   ├── train.py
│   │   └── detect.py
│   ├── hardware/               # Hardware control
│   │   ├── sorting_controller.py
│   │   └── sorting_config.json
│   └── web/                    # Web interface
│       └── dashboard.py
│
├── models/                     # Trained models
│   └── waste_classifier.h5
│
├── outputs/                    # Organized outputs
│   ├── classifications/        # Classification results
│   ├── frames/                 # Captured frames
│   ├── reports/                # Evaluation reports
│   └── plots/                  # Training plots
│
├── tests/                      # Test suite
│   ├── test_waste_classifier.py
│   └── test_integration.py
│
├── docs/                       # Documentation
│   ├── INSTALLATION.md
│   └── USER_GUIDE.md
│
├── deployment/                 # Deployment scripts
│   ├── deploy.py
│   └── deploy_config.json
│
├── metadata/                   # Dataset metadata
│   └── dataset_summary.json
│
├── logs/                       # Application logs
│
├── hyperparameter_tuning.py   # Hyperparameter optimization
├── evaluate_model.py           # Model evaluation
├── cleanup_project.py          # This script
├── demo.py                     # Demo script
├── requirements.txt            # Dependencies
├── README.md                   # Main documentation
├── ACCURACY_REPORT.md          # Accuracy analysis
└── QUICK_SUMMARY.md            # Quick reference
```

## Key Files

### Training & Evaluation
- `src/models/train.py` - Main training script
- `hyperparameter_tuning.py` - Optimize model parameters
- `evaluate_model.py` - Comprehensive evaluation

### Usage
- `demo.py` - Complete system demonstration
- `src/models/detect.py` - Real-time detection
- `src/web/dashboard.py` - Web interface

### Utilities
- `cleanup_project.py` - Project cleanup
- `src/data/data_collector.py` - Data collection

## Removed Files

The following files were removed during cleanup:
- Temporary image files (captured_frame_*.jpg, frame_*.jpg)
- Classification result files (moved to outputs/)
- Redundant scripts (demo_simple.py, train_improved.py, fix_dataset_and_retrain.py)
- Python cache files (__pycache__)

## Best Practices

1. **Keep dataset organized** - One directory per waste category
2. **Use outputs/ for results** - Don't clutter root directory
3. **Regular cleanup** - Run cleanup_project.py periodically
4. **Version control** - Add outputs/ and __pycache__/ to .gitignore
"""
    
    with open('PROJECT_STRUCTURE.md', 'w') as f:
        f.write(structure)
    
    print("[OK] Created PROJECT_STRUCTURE.md")


def main():
    """Main cleanup function"""
    
    print("\n" + "="*70)
    print("WASTE CLASSIFICATION PROJECT - CLEANUP & ORGANIZATION")
    print("="*70)
    print()
    
    print("This script will:")
    print("  1. Remove temporary files (captured frames, classifications)")
    print("  2. Remove redundant scripts")
    print("  3. Clean Python cache")
    print("  4. Organize project structure")
    print("  5. Create clean documentation")
    print()
    
    # Run cleanup
    cleanup_project()
    
    # Organize project
    organize_project()
    
    # Create documentation
    create_clean_structure_doc()
    
    print("="*70)
    print("CLEANUP COMPLETED")
    print("="*70)
    print("\nYour project is now clean and organized!")
    print("Check PROJECT_STRUCTURE.md for the new structure.")
    print()


if __name__ == "__main__":
    main()
