# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Reflask is a Flask-based binary image classification system for automated refund request processing. It uses HOG (Histogram of Oriented Gradients) features with SVM classification to determine if refund requests should be approved or rejected based on visual analysis.

## Architecture

### Core Components

1. **Model Training Pipeline** (`create_model.py`)
   - Preprocesses images to 300x300 grayscale format
   - Extracts HOG features for computer vision
   - Trains SVM classifier with RBF kernel
   - Stores model as `modell.pkl` 
   - Integrates MLflow for experiment tracking
   - Persists metadata to MySQL database

2. **Flask API Server** (`app.py`)
   - `/predict` - Single image classification endpoint
   - `/predict_batch` - Batch processing endpoint
   - Loads pre-trained model from pickle file
   - Handles preprocessing and HOG feature extraction

3. **Batch Processing System** (`batch_predict.py`)
   - Monitors `night_img/` directory for new images
   - Tracks processed files via MySQL to avoid duplicates
   - Saves results to timestamped JSON files in `night_predict/`
   - Designed for scheduled/automated execution

4. **Database Layer** (`dbAccessFunctions.py`)
   - MySQL connector interface for all database operations
   - Manages image metadata, predictions, and processing status
   - Handles environment-based configuration

### Directory Structure
- `data/` - Original training/test images (raw)
- `datapp/` - Preprocessed images (300x300 grayscale)
- `night_img/` - Input directory for batch processing
- `night_predict/` - Output directory for batch results
- `scripts/` - Utility scripts (e.g., uv-auto-python.ps1)

## Development Commands

### Environment Setup
```powershell
# Using uv (preferred)
uv venv
uv sync
uv add <package>

# Run with uv
uv run python app.py
uv run python create_model.py
uv run python batch_predict.py
```

### Database Configuration
Create `.env` file from `.env.example` and set:
```
MyDB_HOST=localhost
MyDB_USER=root
MyDB_PASSWORD=your_password
MyDB_DATABASE=reflask
```

### Model Training
```powershell
# Train the model (creates modell.pkl)
uv run python create_model.py

# View MLflow experiment results
mlflow ui
# Then navigate to http://localhost:5000
```

### Running the Application
```powershell
# Start Flask API server
uv run python app.py
# OR use batch script
.\run_app.bat

# API will be available at http://127.0.0.1:5000
```

### Batch Processing
```powershell
# Place images in night_img/ directory, then:
uv run python batch_predict.py
# OR use batch script (note: hardcoded path)
.\run_batch.bat
```

### API Endpoints

#### Single Prediction
```bash
curl -X POST http://127.0.0.1:5000/predict \
  -F "file=@path/to/image.jpg"
```

#### Batch Prediction
```bash
curl -X POST http://127.0.0.1:5000/predict_batch \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg"
```

### Pre-commit Hooks
```powershell
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Key Technical Details

### Image Processing Pipeline
1. Images must be converted to 300x300 grayscale
2. HOG features extracted with:
   - Orientations: 8
   - Pixels per cell: (16, 16)
   - Cells per block: (1, 1)
3. SVM classifier with RBF kernel (C=1, gamma=0.01)

### Database Schema
The system expects MySQL tables:
- `images` - Image metadata and labels
- `classification_results` - Test results storage
- `predicted_images` - Batch processing tracking

### Environment Variables
Required MySQL configuration via environment variables:
- `MyDB_HOST`
- `MyDB_USER`
- `MyDB_PASSWORD`
- `MyDB_DATABASE` (defaults to "reflask")

## Common Tasks

### Adding New Training Data
1. Place images in `data/train/approved/` or `data/train/rejected/`
2. Uncomment preprocessing lines in `create_model.py` (lines 77-80)
3. Re-run model training: `uv run python create_model.py`

### Modifying Batch Script Paths
The `run_batch.bat` has a hardcoded path that needs updating:
```powershell
# Edit line 2 in run_batch.bat
cd C:\Users\jurda\PycharmProjects\Reflask  # Change to your path
```

### Database Operations
```powershell
# View stored results
uv run python -c "import dbAccessFunctions; dbAccessFunctions.show_table_data(dbAccessFunctions.db_configuration, 'images')"
```

## Dependencies Management

Primary dependencies managed via `uv`:
- Flask (>=3.1.2) - Web framework
- scikit-learn (>=1.7.1) - Machine learning
- scikit-image (>=0.25.2) - Image processing
- mysql-connector-python (>=9.4.0) - Database
- mlflow (~=2.22.2) - Experiment tracking
- numpy, Pillow, requests - Supporting libraries

Update dependencies:
```powershell
uv lock --upgrade
uv sync
```

## Notes

- The model file `modell.pkl` must exist before running the Flask app
- Batch processing tracks processed files to prevent reprocessing
- All timestamps should use UTC (per project rules)
- Follow PEP 8 with 120 character line limit
- Use double quotes for Python strings
- Pre-commit includes gitleaks for security scanning