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

        stage('Verify ML Environment') {
            steps {
                bat 'python src\\test_setup.py'
            }
        }

        stage('Run Automated Tests') {
            steps {
                bat 'python -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker --version'
                bat 'docker build -t resumeiq:%BUILD_NUMBER% .'
            }
        }
    }

    post {
        success {
            echo 'ResumeIQ CI pipeline and Docker image build completed successfully.'
        }

        failure {
            echo 'ResumeIQ pipeline failed. Check the Console Output for the failing stage.'
        }
    }
}
