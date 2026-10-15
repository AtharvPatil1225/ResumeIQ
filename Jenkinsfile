pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                bat 'python --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install --upgrade pip'
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                bat 'python -m pytest -q'
            }
        }
    }

    post {
        success {
            echo 'ResumeIQ CI pipeline completed successfully!'
        }
        failure {
            echo 'ResumeIQ CI pipeline failed. Check the stage logs.'
        }
    }
}
