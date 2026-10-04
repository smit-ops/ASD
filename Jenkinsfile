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
                bat 'python -m compileall gesture_server.py live_gesture.py conversion.py'
            }
        }

        stage('Test') {
            steps {
                echo 'Running basic Python validation...'
                bat 'python -m py_compile gesture_server.py'
                bat 'python -m py_compile live_gesture.py'
                bat 'python -m py_compile conversion.py'
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
                echo 'Deploying Docker container...'
                bat 'docker rm -f hand-gesture-app 2>NUL || exit /b 0'
                bat 'docker run -d --name hand-gesture-app -p 5000:5000 hand-gesture-recognition'
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
