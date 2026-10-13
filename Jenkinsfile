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

        stage('Install ML Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install --upgrade pip'
                bat '"%PYTHON%" -m pip install pandas numpy scikit-learn'
            }
        }

        stage('Test ResumeIQ Setup') {
            steps {
                bat '"%PYTHON%" src\\test_setup.py'
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
