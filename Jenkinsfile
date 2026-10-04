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
                bat 'python -m compileall .'
            }
        }

        stage('Test') {
            steps {
                echo 'Running automated Python validation...'
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
