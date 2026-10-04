pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out project from GitHub...'
                checkout scm
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
            echo 'Pipeline failed. Check the Console Output.'
        }
    }
}
