# Smart Recipe Recommender

An intelligent recipe recommendation system that analyzes your fridge contents and suggests recipes based on available ingredients. Using computer vision and machine learning, this application transforms a simple photo of your ingredients into personalized recipe recommendations.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Data Pipeline](#data-pipeline)

## Overview

This project provides an end-to-end solution for recipe discovery based on real-time ingredient availability. Users can take a photo of their fridge, and the system will:

1. **Capture** - Take or upload a photo of your ingredients
2. **Extract** - Use LLM (Large Language Model) to identify ingredients from the image
3. **Recognize** - Employ ML classification to accurately recognize and confirm ingredients
4. **Recommend** - Suggest the best recipes based on ingredient availability and matching scores

## Features

- **Data**: Custom web scraped datasets for both model training and recipe base
- **Photo Capture**: Click interaction interface for capturing or uploading fridge photos
- **AI-Powered Ingredient Extraction**: LLM integration for intelligent ingredient detection
- **ML Classification**: Custom-trained machine learning model for accurate ingredient recognition
- **Manual Confirmation**: User-friendly interface to verify and adjust detected ingredients
- **Smart Recipe Matching**: Algorithm-based recipe recommendation considering ingredient availability and ingredient importance within recipes
- **Modern UI**: Streamlit-based interface
- **Real-time Processing**: Fast ingredient analysis and recipe matching

## Architecture

The application follows a modular, four-step pipeline architecture:

```
User Photo → LLM Extraction → ML Recognition → Recipe Recommendation
```

### Workflow Steps

1. **Step 1: Photo Capture** (`modules/step1_photo_capture/`)
   - Camera integration or file upload
   - Image preprocessing and optimization

2. **Step 2: Ingredient Selection** (`modules/step2_ingredient_selection/`)
   - Initial ingredient list management
   - User-guided selection interface

3. **Step 3: Ingredient Recognition** (`modules/step3_ingrdient_recognition/`)
   - ML-based classification using custom model
   - Manual confirmation interface for accuracy

4. **Step 4: Recipe Recommendation** (`modules/step4_recipe_recommendation/`)
   - Recipe matching algorithm
   - Scoring based on ingredient availability
   - Display of top recommendations

## Installation

### Setup 

1. **Clone the repository**
   ```bash
   git clone https://github.com/ferdinandfd/Projet-TDLOG-Chosson-Delmas-Fleury.git
   cd Projet-TDLOG-Chosson-Delmas-Fleury
   ```

2. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the ML model**
   ```bash
   python setup/download_model.py
   ```
   This will download the pre-trained ingredient recognition model from HuggingFace.


## Usage

### Running the Application

Start the Streamlit application:

```bash
streamlit run app/app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Using the Interface

1. **Capture Mode**: Take or upload a photo of your fridge/ingredients
2. **Select Mode**: Review and adjust the initial ingredient list
3. **Detect Mode**: ML model analyzes and confirms ingredients with manual verification
4. **Recommend Mode**: View personalized recipe recommendations based on your ingredients

## Project Structure

```
├── app/                              # Main application
│   ├── app.py                       # Streamlit entry point
│   ├── config/                      # Configuration files
│   ├── modules/                     # Core functionality modules
│   │   ├── step1_photo_capture/    # Image capture and upload
│   │   ├── step2_ingredient_selection/  # Ingredient list management
│   │   ├── step3_ingrdient_recognition/ # ML classification
│   │   └── step4_recipe_recommendation/ # Recipe matching engine
│   ├── style/                       # UI styling
│   └── hf_cache/                    # HuggingFace model cache
├── recipes/                         # Recipe data collection
│   ├── pipeline/                    # Web scraping scripts
│   └── output/                      # Scraped recipe data
├── ingredient_images/               # Ingredient image dataset
│   └── pipeline/                    # Image scraping scripts
├── preprocessing/                   # Data preprocessing
│   ├── src/                        # Processing scripts
│   └── output/                     # Processed matrices and datasets
├── setup/                          # Setup and installation scripts
└── requirements.txt                # Python dependencies
```

## Tech Stack

### Frontend & UI
- **Streamlit**: Web application framework
- **Pillow**: Image processing and manipulation

### Machine Learning & AI
- **HuggingFace Transformers**: Pre-trained models and ML pipeline
- **Custom Ingredient Recognition Model**: `antoinechss/ingredient-reco`
- **LLM Integration**: For intelligent ingredient extraction from images

### Data Processing
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Recipe-Ingredient Matrix**: Custom matching algorithm

### Web Scraping
- **Selenium/Browser Automation**: Recipe and ingredient data collection

## Data Pipeline

The project includes comprehensive data collection and preprocessing pipelines:

### Recipe Collection
- Automated web scraping of recipes
- Ingredient extraction and normalization
- Recipe metadata storage

### Ingredient Image Collection
- Automated ingredient image scraping
- Image preprocessing and standardization
- Dataset creation for ML training

### Data Preprocessing
- Recipe-ingredient matrix generation
- Ingredient mapping and normalization
- Data cleaning and filtering
- Output: `recipes_ingredients_matrix.csv` for efficient matching
