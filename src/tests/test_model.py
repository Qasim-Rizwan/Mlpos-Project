#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch, MagicMock

# We need to patch the MLflow imports for unit testing
@pytest.fixture(autouse=True)
def mock_mlflow():
    with patch('src.models.model.mlflow') as mock:
        mock.get_experiment_by_name.return_value = None
        mock.create_experiment.return_value = "1"
        mock.start_run.return_value.__enter__.return_value.info.run_id = "test-run-id"
        yield mock

# Import the model class after patching MLflow
from src.models.model import MLModel

@pytest.fixture
def sample_data():
    """Generate sample data for testing."""
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.randn(100)
    feature_names = [f'feature_{i}' for i in range(5)]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    return df

@pytest.fixture
def model():
    """Create model instance for testing."""
    return MLModel(experiment_name="test-experiment")

def test_model_initialization(model):
    """Test model initialization."""
    assert model is not None
    assert model.model is None
    assert model.experiment_name == "test-experiment"

def test_preprocess_data(model, sample_data):
    """Test data preprocessing."""
    X_train, X_test, y_train, y_test, feature_names = model.preprocess_data(sample_data, 'target')
    
    # Check shapes
    assert X_train.shape[0] + X_test.shape[0] == sample_data.shape[0]
    assert X_train.shape[1] == 5  # Number of features
    assert len(y_train) == X_train.shape[0]
    assert len(y_test) == X_test.shape[0]
    
    # Check feature names
    assert len(feature_names) == 5
    assert all(f'feature_{i}' in feature_names for i in range(5))

def test_train_and_predict(model, sample_data):
    """Test model training and prediction."""
    # Preprocess data
    X_train, X_test, y_train, y_test, _ = model.preprocess_data(sample_data, 'target')
    
    # Train model
    run_id = model.train(X_train, y_train, params={'n_estimators': 10, 'random_state': 42})
    assert run_id == "test-run-id"
    
    # Check if model was trained
    assert model.model is not None
    
    # Make predictions
    predictions = model.predict(X_test)
    assert len(predictions) == len(y_test)
    assert all(isinstance(pred, (int, float, np.int64, np.float64)) for pred in predictions)

def test_save_and_load_model(model, sample_data, tmp_path):
    """Test saving and loading model."""
    # Preprocess data
    X_train, X_test, y_train, y_test, _ = model.preprocess_data(sample_data, 'target')
    
    # Train model
    model.train(X_train, y_train, params={'n_estimators': 10, 'random_state': 42})
    
    # Save model
    model_path = os.path.join(tmp_path, "model.pkl")
    model.save(model_path)
    assert os.path.exists(model_path)
    
    # Create new model instance
    new_model = MLModel(experiment_name="test-experiment")
    
    # Load model
    new_model.load(model_path)
    assert new_model.model is not None
    
    # Make predictions with both models on same data
    original_predictions = model.predict(X_test)
    loaded_predictions = new_model.predict(X_test)
    
    # Check predictions are the same
    np.testing.assert_array_equal(original_predictions, loaded_predictions) 