"""
Unified ML Classifier for ingredient recognition using Hugging Face model.
Combines real ML inference with workflow integration.
Falls back to mock predictions when PyTorch is not available.
"""

import logging
from typing import List, Dict
from PIL import Image

# Import optional dependency for streamlit integration
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

# Import optional ML dependencies (PyTorch and transformers)
TORCH_AVAILABLE = False
torch = None
AutoModelForImageClassification = None
AutoImageProcessor = None

try:
    import torch
    from transformers import AutoModelForImageClassification, AutoImageProcessor
    TORCH_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("PyTorch and transformers available")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("PyTorch or transformers not available - using fallback mode")

# Set up logging
logging.basicConfig(level=logging.INFO)


class IngredientClassifier:
    """
    Unified classifier that handles ML-based ingredient classification
    with Hugging Face model integration and user validation workflow
    """
    
    def __init__(self, model_name="antoinechss/ingredient-reco"):
        self.model_name = model_name
        self.model = None
        self.processor = None
        self.device = "cpu"
        
        # Initialize ingredient vocabulary for fallback
        self.fallback_ingredient_vocabulary = [
            "apple", "banana", "bell_pepper", "broccoli", "cabbage", "carrot",
            "cauliflower", "celery", "corn", "cucumber", "eggplant", "garlic",
            "ginger", "lemon", "lettuce", "lime", "mushroom", "onion", "orange",
            "peas", "potato", "pumpkin", "radish", "spinach", "tomato", "zucchini",
            "avocado", "beans", "beetroot", "cherry", "chili", "coconut", "grapes",
            "kiwi", "mango", "papaya", "pineapple", "strawberry", "watermelon",
            "asparagus", "brussels_sprouts", "leek", "parsnip", "turnip", "artichoke"
        ]
        
        # Load model
        self.model_loaded = self.load_model_with_retries()
    
    def load_model_with_retries(self):
        """Load the HuggingFace model from cache"""
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available - using fallback predictions")
            return False
            
        cache_dirs = ["./app/hf_cache", "./hf_cache"]
        
        for cache_dir in cache_dirs:
            try:
                logger.info(f"Loading {self.model_name} from {cache_dir}")
                
                # Load processor from cache
                logger.info("Loading image processor from cache")
                self.processor = AutoImageProcessor.from_pretrained(
                    self.model_name,
                    cache_dir=cache_dir,
                    local_files_only=True
                )
                
                # Load model from cache
                logger.info("Loading model weights from cache")
                self.model = AutoModelForImageClassification.from_pretrained(
                    self.model_name,
                    dtype=torch.float32,
                    cache_dir=cache_dir,
                    local_files_only=True
                )
                
                # Move to CPU and set to evaluation mode
                self.model.to(self.device)
                self.model.eval()
                
                logger.info(f"Model loaded successfully from {cache_dir}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load from {cache_dir}: {e}")
                continue
        
        # If all cache directories failed
        logger.error("All cache directories failed - no model loaded")
        return False
    
    def setup_ingredient_labels(self):
        return
    
    def classify_ingredients_batch(self, images):
        """
        Classify ingredients using real ML model or fallback
        
        Args:
            images: List of PIL Images or image paths
            
        Returns:
            List of prediction results
        """
        if not images:
            return []
        
        if self.model_loaded and self.model is not None and self.processor is not None:
            return self._real_ml_prediction(images)
        else:
            return self._fallback_prediction(images)
    
    def _real_ml_prediction(self, images):
        """Real ML prediction using HuggingFace model"""
        try:
            logger.info(f"Running real ML inference on {len(images)} images")
            
            # Process images for the model
            processed_images = []
            for img in images:
                if isinstance(img, str):
                    img = Image.open(img).convert('RGB')
                elif hasattr(img, 'convert'):
                    img = img.convert('RGB')
                else:
                    logger.warning(f"Unknown image type: {type(img)}")
                    continue
                
                processed_images.append(img)
            
            if not processed_images:
                return []
            
            # Preprocess batch
            inputs = self.processor(processed_images, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Process results
            results = []
            for i, probs in enumerate(probabilities):
                top_probs, top_indices = torch.topk(probs, min(3, len(probs)))
                
                predictions = []
                for prob, idx in zip(top_probs, top_indices):
                    label = self.model.config.id2label.get(
                        idx.item(), 
                        f"class_{idx.item()}"
                    )
                    confidence = float(prob.item())
                    
                    predictions.append({
                        'label': label,
                        'confidence': confidence
                    })
                
                results.append(predictions)
            
            logger.info(f"ML predictions complete for {len(results)} images")
            return results
            
        except Exception as e:
            logger.error(f"ML inference failed: {e}")
            raise RuntimeError("ML inference failed — refusing to return random predictions")

    
    def _fallback_prediction(self, images):
        """Fallback prediction when real ML is not available"""
        import random
        
        logger.info(f"Using fallback prediction for {len(images)} images")
        
        results = []
        for i, img in enumerate(images):
            # Generate realistic fallback predictions from ingredient vocabulary
            selected_ingredients = random.sample(self.fallback_ingredient_vocabulary, min(3, len(self.fallback_ingredient_vocabulary)))
            confidences = sorted([random.uniform(0.4, 0.8) for _ in range(len(selected_ingredients))], reverse=True)
            
            predictions = []
            for ingredient, confidence in zip(selected_ingredients, confidences):
                predictions.append({
                    'label': ingredient,
                    'confidence': confidence
                })
            
            results.append(predictions)
        
        return results
    
    def analyze_all_ingredients(self, extracted_ingredients: List[Dict]) -> List[Dict]:
        """
        Run ML analysis on all extracted ingredients with progress tracking
        
        Args:
            extracted_ingredients: List of extracted ingredient data
            
        Returns:
            List of ML prediction results
        """
        if not extracted_ingredients:
            return []
        
        results = []
        
        # Progress tracking (only if streamlit available)
        if STREAMLIT_AVAILABLE and st:
            progress_bar = st.progress(0)
            status_text = st.empty()
        else:
            progress_bar = None
            status_text = None
        
        # Extract images from ingredient data
        images = []
        for ingredient in extracted_ingredients:
            if "image" in ingredient:
                images.append(ingredient["image"])
            else:
                logger.warning(f"No image found in ingredient data: {ingredient}")
        
        if not images:
            if progress_bar:
                progress_bar.empty()
            if status_text:
                status_text.empty()
            return []
        
        # Run batch classification
        if status_text:
            status_text.text("Running ML analysis on ingredients...")
        predictions = self.classify_ingredients_batch(images)
        
        # Combine predictions with original ingredient data
        for i, (ingredient, preds) in enumerate(zip(extracted_ingredients, predictions)):
            if preds:  # If we have predictions
                main_prediction = preds[0]
                alternatives = preds[1:] if len(preds) > 1 else []
                
                result = {
                    "index": ingredient.get("index", i),
                    "coordinates": ingredient.get("coordinates", (0, 0)),
                    "filepath": ingredient.get("filepath", ""),
                    "original_image": ingredient["image"],
                    "prediction": main_prediction["label"],
                    "confidence": main_prediction["confidence"],
                    "alternatives": [
                        {"label": alt["label"], "confidence": alt["confidence"]} 
                        for alt in alternatives
                    ],
                    "user_corrected": False,
                    "user_validated": False
                }
            else:
                # No predictions available
                result = {
                    "index": ingredient.get("index", i),
                    "coordinates": ingredient.get("coordinates", (0, 0)),
                    "filepath": ingredient.get("filepath", ""),
                    "original_image": ingredient["image"],
                    "prediction": "unknown",
                    "confidence": 0.0,
                    "alternatives": [],
                    "user_corrected": False,
                    "user_validated": False
                }
            
            results.append(result)
            if progress_bar:
                progress_bar.progress((i + 1) / len(extracted_ingredients))
        
        # Remove progress UI elements
        if progress_bar:
            progress_bar.empty()
        if status_text:
            status_text.empty()
        
        return results
    
    def validate_prediction(self, prediction: Dict, user_correction: str) -> Dict:
        """
        Validate and potentially correct an ML prediction
        
        Args:
            prediction: Original ML prediction dict
            user_correction: User's correction text
            
        Returns:
            Updated prediction dict
        """
        validated = prediction.copy()
        
        if user_correction and user_correction.strip():
            validated.update({
                "original_prediction": prediction["prediction"],
                "prediction": user_correction.strip().lower(),
                "user_corrected": True,
                "user_validated": True
            })
        else:
            validated.update({
                "user_corrected": False,
                "user_validated": True
            })
        
        return validated
    
    def initialize_session_state(self):
        """Initialize session state for ML classification"""
        if "ml_results" not in st.session_state:
            st.session_state.ml_results = []
        if "validated_ingredients" not in st.session_state:
            st.session_state.validated_ingredients = []
        if "analysis_complete" not in st.session_state:
            st.session_state.analysis_complete = False
    
    def get_status(self):
        """Get classifier status information"""
        return {
            'model_loaded': self.model_loaded and self.model is not None,
            'model_name': self.model_name,
            'device': self.device,
            'num_classes': len(self.model.config.id2label) if self.model else 0,
            'prediction_mode': 'REAL_ML' if self.model_loaded else 'NO_MODEL'
        }


@st.cache_resource
def get_classifier():
    return IngredientClassifier()

def classify_ingredients(images):
    """
    Main function to classify ingredients
    
    Args:
        images: List of PIL Images or image paths
        
    Returns:
        List of prediction results
    """
    classifier = get_classifier()
    return classifier.classify_ingredients_batch(images)

def get_model_status():
    """Get model status information"""
    classifier = get_classifier()
    return classifier.get_status()
