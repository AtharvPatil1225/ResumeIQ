
pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Program Files\\WindowsApps\\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\\python3.13.exe'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                bat '"%PYTHON%" --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install --upgrade pip'
                bat '"%PYTHON%" -m pip install -r requirements.txt'
            }
        }

        stage('Verify ML Environment') {
            steps {
                bat '"%PYTHON%" src\\test_setup.py'
            }
        }

        stage('Run Automated Tests') {
            steps {
                bat '"%PYTHON%" -m pytest -v'
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
