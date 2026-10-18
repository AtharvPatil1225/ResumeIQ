
pipeline {
    agent any

    environment {
        // Override PYTHON in your Jenkins node configuration or leave as
        // the system default.  Do NOT hardcode a machine-specific path here.
        PYTHON = "${env.PYTHON ?: 'python'}"
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
                // pytest.ini sets pythonpath = src automatically.
                // All test files under src/ are discovered automatically.
                bat '"%PYTHON%" -m pytest -v --tb=short'
            }
        }

        stage('Generate Synthetic Training Data') {
            steps {
                bat '"%PYTHON%" src\\generate_training_data.py'
            }
        }

        stage('Train ML Models') {
            steps {
                bat '"%PYTHON%" src\\train_model.py'
            }
        }

        stage('Build Docker Image') {
            when {
                // Only attempt Docker build when Docker is available on the agent.
                expression {
                    try {
                        bat(script: 'docker --version', returnStatus: true) == 0
                    } catch (ignored) {
                        false
                    }
                }
            }
            steps {
                bat 'docker build -t resumeiq:%BUILD_NUMBER% .'
            }
        }
    }

    post {
        success {
            echo 'ResumeIQ CI pipeline completed successfully.'
        }
        failure {
            echo 'ResumeIQ pipeline failed. Check the Console Output for details.'
        }
    }
}
