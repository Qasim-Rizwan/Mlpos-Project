#!/usr/bin/env python3
import os
import json
import logging
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
from models.model import MLModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ML Model Prediction API",
    description="API for making predictions with ML model",
    version="1.0.0"
)

# Model configuration
MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")

# Data models
class PredictionFeatures(BaseModel):
    """Input features for prediction."""
    features: Dict[str, float] = Field(..., example={"feature_0": 0.1, "feature_1": -0.5, "feature_2": 0.7})

class PredictionResponse(BaseModel):
    """Prediction response."""
    prediction: float
    model_version: str
    prediction_id: str

# Initialize model as None to load it lazily
model_instance = None

def get_model():
    """Get model instance, loading it if necessary."""
    global model_instance
    if model_instance is None:
        try:
            logger.info(f"Loading model from {MODEL_PATH}")
            model_instance = MLModel()
            model_instance.load(MODEL_PATH)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise HTTPException(status_code=500, detail=f"Could not load model: {str(e)}")
    return model_instance

@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "ML Model Prediction API"}

@app.get("/health")
def health():
    """Health check endpoint."""
    model = get_model()
    if model.model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    return {"status": "healthy", "model_loaded": True}

@app.post("/predict", response_model=PredictionResponse)
def predict(features: PredictionFeatures, model: MLModel = Depends(get_model)):
    """Make prediction with the model."""
    try:
        # Convert input features to dataframe
        df = pd.DataFrame([features.features])
        
        # Make prediction
        prediction = model.predict(df)[0]
        
        # Create response
        response = {
            "prediction": float(prediction),
            "model_version": os.path.basename(MODEL_PATH),
            "prediction_id": str(hash(frozenset(features.features.items())))
        }
        
        return response
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Error making prediction: {str(e)}")

@app.post("/batch-predict")
def batch_predict(features_batch: List[PredictionFeatures], model: MLModel = Depends(get_model)):
    """Make batch predictions with the model."""
    try:
        # Convert input features to dataframe
        feature_dicts = [f.features for f in features_batch]
        df = pd.DataFrame(feature_dicts)
        
        # Make predictions
        predictions = model.predict(df).tolist()
        
        # Create response
        response = {
            "predictions": predictions,
            "model_version": os.path.basename(MODEL_PATH),
            "count": len(predictions)
        }
        
        return response
    except Exception as e:
        logger.error(f"Error making batch prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Error making batch prediction: {str(e)}")

if __name__ == "__main__":
    # Run the API server
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False) 