
pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Validating Python project...'
                bat 'python --version'
                bat 'python -m compileall .'
            }
        }

        stage('Test') {
            steps {
                echo 'Running project tests...'
                bat 'python -m compileall gesture_server.py live_gesture.py conversion.py'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                bat 'docker build -t hand-gesture-recognition .'
            }
        }

        stage('Docker Deployment') {
            steps {
                echo 'Starting Docker container...'
                bat 'docker run -d --name hand-gesture-app -p 5000:5000 hand-gesture-recognition'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the console output.'
        }
    }
}
