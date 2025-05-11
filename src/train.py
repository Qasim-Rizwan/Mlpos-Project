#!/usr/bin/env python3
import os
import argparse
import pandas as pd
import yaml
from datetime import datetime
from models.model import MLModel

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Train a machine learning model")
    parser.add_argument("--data", type=str, required=True, help="Path to the input data CSV file")
    parser.add_argument("--target", type=str, required=True, help="Name of the target column in the dataset")
    parser.add_argument("--experiment", type=str, default="ml-pipeline", help="MLflow experiment name")
    parser.add_argument("--config", type=str, default=None, help="Path to model config YAML file")
    parser.add_argument("--output", type=str, default="models", help="Directory to save the trained model")
    
    return parser.parse_args()

def load_config(config_path):
    """Load model configuration from YAML file."""
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    return None

def main():
    """Main function to train the model."""
    args = parse_args()
    
    # Create model instance
    model = MLModel(experiment_name=args.experiment)
    
    # Load configuration if provided
    config = load_config(args.config)
    model_params = config.get("model_params", None) if config else None
    
    # Load and preprocess data
    df = model.load_data(args.data)
    X_train, X_test, y_train, y_test, feature_names = model.preprocess_data(df, args.target)
    
    # Train and evaluate model
    run_id = model.train(X_train, y_train, params=model_params)
    model.evaluate(X_test, y_test, run_id)
    
    # Save model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_filename = f"model_{timestamp}.pkl"
    os.makedirs(args.output, exist_ok=True)
    model_path = os.path.join(args.output, model_filename)
    model.save(model_path)
    
    print(f"Model training completed successfully. Model saved to {model_path}")
    return model_path

if __name__ == "__main__":
    main() 