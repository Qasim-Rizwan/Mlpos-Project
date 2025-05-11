from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Define default arguments
default_args = {
    'owner': 'mlops',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'ml_pipeline',
    default_args=default_args,
    description='ML Pipeline for data processing, training, and deployment',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['ml', 'pipeline'],
)

# Define the data paths
RAW_DATA_PATH = '/data/raw'
PROCESSED_DATA_PATH = '/data/processed'
MODEL_PATH = '/models'

# Data extraction function
def extract_data():
    """Extract data from source."""
    # In a real scenario, this would pull data from a database or API
    # For this example, we'll simulate by generating some random data
    
    print("Extracting data...")
    # Create data directory if it doesn't exist
    os.makedirs(RAW_DATA_PATH, exist_ok=True)
    
    # Generate synthetic data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    # Create features
    X = np.random.randn(n_samples, n_features)
    
    # Create target (simple linear model with noise)
    y = X.dot(np.random.randn(n_features)) + 0.5 * np.random.randn(n_samples)
    
    # Create DataFrame
    feature_names = [f'feature_{i}' for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    
    # Save to CSV
    output_path = os.path.join(RAW_DATA_PATH, f'data_{datetime.now().strftime("%Y%m%d")}.csv')
    df.to_csv(output_path, index=False)
    print(f"Data extracted and saved to {output_path}")
    
    return output_path

# Data transformation function
def transform_data(ti):
    """Transform and clean the data."""
    # Get the extracted data path from XCom
    input_path = ti.xcom_pull(task_ids='extract')
    
    print(f"Transforming data from {input_path}...")
    # Create processed data directory if it doesn't exist
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    
    # Load the data
    df = pd.read_csv(input_path)
    
    # Perform transformations (in a real scenario, this would be more complex)
    # For example: handling missing values, scaling, feature engineering, etc.
    
    # Drop any rows with missing values
    df = df.dropna()
    
    # Add some derived features
    df['feature_sum'] = df.iloc[:, :-1].sum(axis=1)
    df['feature_mean'] = df.iloc[:, :-1].mean(axis=1)
    
    # Save processed data
    output_path = os.path.join(PROCESSED_DATA_PATH, f'processed_{datetime.now().strftime("%Y%m%d")}.csv')
    df.to_csv(output_path, index=False)
    print(f"Data transformed and saved to {output_path}")
    
    return output_path

# Define the tasks
extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

train_task = BashOperator(
    task_id='train',
    bash_command='python /app/src/train.py --data "{{ ti.xcom_pull(task_ids="transform") }}" --target "target" --output /models',
    dag=dag,
)

deploy_task = BashOperator(
    task_id='deploy',
    bash_command='MODEL_PATH=$(ls -t /models/model_*.pkl | head -1) && cp $MODEL_PATH /models/model.pkl',
    dag=dag,
)

# Define the task dependencies
extract_task >> transform_task >> train_task >> deploy_task 