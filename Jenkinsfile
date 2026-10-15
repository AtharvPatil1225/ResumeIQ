
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
                bat '"%PYTHON%" -m pip install pandas numpy scikit-learn joblib pymupdf pytest'
            }
        }

        stage('Verify ML Environment') {
            steps {
                bat '"%PYTHON%" src\\test_setup.py'
            }
        }

        stage('Run Automated Tests') {
            steps {
                bat 'set "PYTHONPATH=%WORKSPACE%\\src"&& "%PYTHON%" -m pytest -v src\\test_matching_engine.py src\\test_skill_extractor.py src\\test_folder_inspection.py'
            }
        }
    }

    post {
        success {
            echo 'ResumeIQ CI completed: dependencies and automated tests passed.'
        }

        failure {
            echo 'ResumeIQ CI failed. Check the console output for the failing stage.'
        }
    }
}
