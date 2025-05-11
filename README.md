# Innovate Analytics MLOps Project

This repository contains an end-to-end machine learning pipeline for Innovate Analytics Inc., including data processing, model training, and deployment infrastructure.

## Project Overview

This project implements a complete MLOps workflow with:

- Sprint planning and team collaboration (GitHub Issues)
- Environment management (Git branching strategy)
- Automated data processing pipeline (Airflow)
- ML model development with scikit-learn
- Experiment tracking with MLflow
- Data versioning with DVC
- Automated testing and code quality checks (GitHub Actions)
- Containerization with Docker
- CI/CD pipeline with Jenkins
- Kubernetes deployment

## Repository Structure

```
├── .github/workflows/    # GitHub Actions workflows for CI
├── dags/                 # Airflow DAG definitions
├── k8s/                  # Kubernetes configuration files
├── src/                  # Source code
│   ├── data/             # Data processing scripts
│   ├── models/           # ML model implementations
│   ├── pipeline/         # Pipeline orchestration code
│   ├── utils/            # Utility functions
│   └── tests/            # Unit tests
├── notebooks/            # Jupyter notebooks for experimentation
├── Dockerfile            # Docker image definition
├── Jenkinsfile           # Jenkins pipeline definition
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Branching Strategy

- `main`: Production environment (protected)
- `test`: Testing/staging environment (protected)
- `dev`: Development environment
- feature branches: Used for individual feature development

## Setup and Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/Qasim-Rizwan/Mlpos-Project.git
   cd Mlpos-Project
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running in Docker

1. Build the Docker image:
   ```bash
   docker build -t ml-model-api:latest .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 ml-model-api:latest
   ```

### Deployment to Kubernetes

1. Apply the Kubernetes configurations:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

## CI/CD Pipeline

The CI/CD pipeline consists of:

1. **Linting & Unit Tests**: Triggered on pushes to `dev` and PRs to `test`/`main`
2. **Docker Build**: Builds and tags the application image
3. **Docker Push**: Pushes the image to Docker Hub
4. **Deployment**: Deploys to Kubernetes when code is merged to `main`

## Data Pipeline

The data pipeline is orchestrated using Airflow DAGs and includes:

1. Data extraction from sources
2. Data transformation and cleaning
3. Feature engineering
4. Model training and evaluation
5. Model deployment

## Model Serving API

The model is served via a FastAPI application with endpoints:

- `GET /health`: Health check endpoint
- `POST /predict`: Make a single prediction
- `POST /batch-predict`: Make predictions for multiple samples

## Team Collaboration

Team members use the GitHub Issues system for sprint planning and task tracking. 