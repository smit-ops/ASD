pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out project from GitHub...'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Checking Python environment...'
                bat 'python --version'
                bat 'python -m compileall live_gesture.py conversion.py'
            }
        }

        stage('Test') {
            steps {
                echo 'Running Python validation...'
                bat 'python -m py_compile live_gesture.py'
                bat 'python -m py_compile conversion.py'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image for Hand Gesture Recognition...'
                bat 'docker build -t hand-gesture-recognition .'
            }
        }

        stage('Docker Deployment') {
            steps {
                echo 'Starting Hand Gesture Recognition application...'
                bat 'docker rm -f hand-gesture-app 2>NUL || exit /b 0'
                bat 'docker run -d --name hand-gesture-app hand-gesture-recognition'
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the Jenkins Console Output.'
        }
    }
}
