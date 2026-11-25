pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'python -m pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
                sh 'cd frontend && npm ci'
            }
        }

        stage('Build Frontend') {
            steps {
                sh 'cd frontend && npm run build'
            }
        }

        stage('Test & Coverage') {
            steps {
                sh 'python -m pytest tests/unit tests/integration -v --cov=backend --cov=recommendation_engine --cov=database --cov-report=xml:coverage.xml --cov-fail-under=80'
            }
        }

        stage('AI Offline Evaluation') {
            steps {
                sh 'python -m database.seed'
                sh 'python -m recommendation_engine.evaluator'
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                echo 'Running SonarQube Scanner (configure SONAR_HOST_URL and SONAR_TOKEN in Jenkins credentials)'
                // sh 'sonar-scanner'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t tunetrail:latest .'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
        }
    }
}
