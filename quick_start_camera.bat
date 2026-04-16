@echo off
echo ========================================
echo Waste Classification - Camera Evaluation
echo ========================================
echo.

cd /d "%~dp0"

echo Checking if model exists...
if not exist "models\waste_classifier.h5" (
    echo [ERROR] Model not found!
    echo Please train the model first:
    echo   python train_optimized.py
    echo.
    pause
    exit /b 1
)

echo [OK] Model found!
echo.
echo Starting camera evaluation...
echo.
echo Controls:
echo   S - Save prediction
echo   P - Pause/Resume
echo   Q - Quit
echo.
echo ========================================
echo.

python camera_evaluation_advanced.py

pause
