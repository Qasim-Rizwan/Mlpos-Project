pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'innovateanalytics'
        IMAGE_NAME = 'ml-model-api'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        DOCKER_CREDENTIALS_ID = 'dockerhub-credentials'
        K8S_CONFIG_ID = 'k8s-config'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Lint') {
            steps {
                sh 'flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics'
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh 'pytest -v src/tests/'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    def dockerImage = docker.build("${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }
        
        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIALS_ID) {
                        def dockerImage = docker.image("${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}")
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            when {
                branch 'main'
            }
            steps {
                script {
                    withCredentials([file(credentialsId: K8S_CONFIG_ID, variable: 'KUBECONFIG')]) {
                        sh """
                            envsubst < k8s/deployment.yaml > k8s/deployment-rendered.yaml
                            kubectl apply -f k8s/deployment-rendered.yaml
                            kubectl apply -f k8s/service.yaml
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Clean up workspace
            cleanWs()
        }
        success {
            echo 'Pipeline successfully completed!'
        }
        failure {
            echo 'Pipeline failed!'
            // Send notification on failure
            // mail to: 'team@innovateanalytics.com', subject: 'Pipeline Failed', body: "The pipeline ${env.JOB_NAME} failed at ${env.BUILD_URL}"
        }
    }
} 