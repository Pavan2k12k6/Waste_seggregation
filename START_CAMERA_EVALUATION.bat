@echo off
title Waste Classification - Camera Evaluation
color 0A

cd /d "%~dp0"

:menu
cls
echo ========================================
echo   WASTE CLASSIFICATION SYSTEM
echo   Camera Evaluation Menu
echo ========================================
echo.
echo 1. Basic Camera Evaluation
echo 2. Advanced Camera Evaluation (Recommended)
echo 3. Test Camera Availability
echo 4. View Saved Predictions
echo 5. Check Model Status
echo 6. Exit
echo.
echo ========================================
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto basic
if "%choice%"=="2" goto advanced
if "%choice%"=="3" goto test
if "%choice%"=="4" goto view
if "%choice%"=="5" goto status
if "%choice%"=="6" goto end

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:basic
cls
echo Starting Basic Camera Evaluation...
echo.
python camera_evaluation.py
pause
goto menu

:advanced
cls
echo Starting Advanced Camera Evaluation...
echo.
python camera_evaluation_advanced.py
pause
goto menu

:test
cls
echo Testing Camera Availability...
echo.
python camera_evaluation.py --test
pause
goto menu

:view
cls
echo Opening saved predictions folder...
if exist "outputs\camera_predictions" (
    explorer "outputs\camera_predictions"
) else (
    echo No predictions saved yet.
    echo Run camera evaluation and press 'S' to save predictions.
)
pause
goto menu

:status
cls
echo ========================================
echo   MODEL STATUS
echo ========================================
echo.
if exist "models\waste_classifier.h5" (
    echo [OK] Main model found: models\waste_classifier.h5
) else (
    echo [X] Main model not found!
)
echo.
if exist "models\waste_classifier_optimized.h5" (
    echo [OK] Optimized model found: models\waste_classifier_optimized.h5
) else (
    echo [X] Optimized model not found!
)
echo.
if exist "models\training_log.csv" (
    echo [OK] Training log found
) else (
    echo [X] Training log not found
)
echo.
if exist "models\accuracy_report.json" (
    echo [OK] Accuracy report found
) else (
    echo [X] Accuracy report not found
)
echo.
echo ========================================
pause
goto menu

:end
cls
echo Thank you for using Waste Classification System!
timeout /t 2 >nul
exit
