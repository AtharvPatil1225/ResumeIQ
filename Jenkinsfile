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

        stage('Install ML Dependencies') {
            steps {
                bat 'python -m pip install --upgrade pip'
                bat 'python -m pip install pandas numpy scikit-learn'
            }
        }

        stage('Test ResumeIQ Setup') {
            steps {
                bat 'python src/test_setup.py'
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
