#!/usr/bin/env python3
import os
import pickle
import logging
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import mlflow.sklearn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set MLflow tracking URI
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

class MLModel:
    def __init__(self, experiment_name="ml-pipeline"):
        """Initialize the ML model."""
        self.model = None
        self.experiment_name = experiment_name
        self._ensure_experiment_exists()
        
    def _ensure_experiment_exists(self):
        """Create MLflow experiment if it doesn't exist yet."""
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        if experiment is None:
            mlflow.create_experiment(self.experiment_name)
        self.experiment_id = mlflow.get_experiment_by_name(self.experiment_name).experiment_id
    
    def load_data(self, data_path):
        """Load dataset from CSV file."""
        logger.info(f"Loading data from {data_path}")
        try:
            df = pd.read_csv(data_path)
            logger.info(f"Data loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def preprocess_data(self, df, target_column, test_size=0.2, random_state=42):
        """Preprocess data and split into train/test sets."""
        logger.info("Preprocessing data")
        try:
            # For simplicity, we'll assume all other columns are features
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Handle categorical variables (for simplicity, we'll just drop them)
            X = X.select_dtypes(include=['int64', 'float64'])
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            logger.info(f"Data split into {X_train.shape[0]} training and {X_test.shape[0]} test samples")
            return X_train, X_test, y_train, y_test, X.columns.tolist()
        except Exception as e:
            logger.error(f"Error preprocessing data: {e}")
            raise
    
    def train(self, X_train, y_train, params=None):
        """Train the model with given parameters."""
        logger.info("Training model")
        with mlflow.start_run(experiment_id=self.experiment_id) as run:
            # Set default parameters if none provided
            if params is None:
                params = {
                    "n_estimators": 100,
                    "max_depth": 10,
                    "min_samples_split": 2,
                    "random_state": 42
                }
            
            # Log parameters
            for param_name, param_value in params.items():
                mlflow.log_param(param_name, param_value)
            
            # Train model
            self.model = RandomForestRegressor(**params)
            self.model.fit(X_train, y_train)
            
            # Log model
            mlflow.sklearn.log_model(self.model, "model")
            
            logger.info(f"Model trained successfully. Run ID: {run.info.run_id}")
            return run.info.run_id
    
    def evaluate(self, X_test, y_test, run_id=None):
        """Evaluate the model and log metrics."""
        logger.info("Evaluating model")
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Get active run or start a new one
        if run_id:
            with mlflow.start_run(run_id=run_id):
                y_pred = self.model.predict(X_test)
                self._log_metrics(y_test, y_pred)
        else:
            with mlflow.start_run(experiment_id=self.experiment_id) as run:
                y_pred = self.model.predict(X_test)
                self._log_metrics(y_test, y_pred)
                run_id = run.info.run_id
        
        return run_id
    
    def _log_metrics(self, y_true, y_pred):
        """Log evaluation metrics to MLflow."""
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        
        logger.info(f"Model evaluation: MSE={mse:.4f}, RMSE={rmse:.4f}, R2={r2:.4f}")
    
    def save(self, model_path):
        """Save model to file."""
        logger.info(f"Saving model to {model_path}")
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        logger.info("Model saved successfully")
    
    def load(self, model_path):
        """Load model from file."""
        logger.info(f"Loading model from {model_path}")
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def predict(self, X):
        """Make predictions with trained model."""
        if self.model is None:
            raise ValueError("Model not trained yet")
        return self.model.predict(X)


if __name__ == "__main__":
    # This is a simple example of how to use the model class
    try:
        # Create model
        model = MLModel(experiment_name="example-experiment")
        
        # Generate some random data for demonstration
        from sklearn.datasets import make_regression
        X, y = make_regression(n_samples=1000, n_features=10, noise=0.1, random_state=42)
        df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
        df["target"] = y
        
        # Save sample data
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/sample_data.csv", index=False)
        
        # Load and preprocess data
        df = model.load_data("data/sample_data.csv")
        X_train, X_test, y_train, y_test, feature_names = model.preprocess_data(df, "target")
        
        # Train model
        run_id = model.train(X_train, y_train)
        
        # Evaluate model
        model.evaluate(X_test, y_test, run_id)
        
        # Save model
        model.save("models/model.pkl")
        
        logger.info("Example completed successfully")
    except Exception as e:
        logger.error(f"Error in example: {e}") 