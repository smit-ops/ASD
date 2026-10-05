pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out project from GitHub...'
                checkout scm
            }
        }

        stage('Test') {
            steps {
                echo 'Running project tests...'
                bat '''
                    if not exist index.html exit /b 1
                    if not exist images exit /b 1
                    if not exist real_fruits exit /b 1
                    if not exist static exit /b 1
                    echo All required project files are present.
                    echo Test phase completed successfully!
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                bat 'docker build -t hand-gesture-recognition .'
            }
        }

        stage('Test EC2 SSH') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    bat '''
                        ssh -o StrictHostKeyChecking=no ec2-user@3.26.159.222 "echo EC2 SSH connection successful"
                    '''
                }
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
