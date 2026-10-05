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
                echo 'Building Docker image using Docker Desktop...'

                bat '''
                    docker build -t hand-gesture-recognition:latest .
                '''
            }
        }

        stage('Verify Docker Image') {
            steps {
                echo 'Verifying Docker image created by Docker Desktop...'

                bat '''
                    docker image inspect hand-gesture-recognition:latest
                '''
            }
        }

        stage('Test EC2 SSH') {
            steps {
                echo 'Testing SSH connection to AWS EC2...'

                sshagent(['ec2-ssh-key']) {
                    bat '''
                        ssh -o StrictHostKeyChecking=no ec2-user@3.26.159.222 "echo EC2 SSH connection successful"
                    '''
                }
            }
        }

        stage('Save Docker Image') {
            steps {
                echo 'Saving the Docker Desktop image as a TAR file...'

                bat '''
                    docker save -o hand-gesture-recognition.tar hand-gesture-recognition:latest
                '''
            }
        }

        stage('Transfer Image to EC2') {
            steps {
                echo 'Transferring the exact Docker image from Docker Desktop to EC2...'

                sshagent(['ec2-ssh-key']) {
                    bat '''
                        scp -o StrictHostKeyChecking=no hand-gesture-recognition.tar ec2-user@3.26.159.222:/home/ec2-user/
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo 'Loading Docker image on EC2 and deploying the new container...'

                sshagent(['ec2-ssh-key']) {
                    bat '''
                        ssh -o StrictHostKeyChecking=no ec2-user@3.26.159.222 "docker load -i /home/ec2-user/hand-gesture-recognition.tar"

                        ssh -o StrictHostKeyChecking=no ec2-user@3.26.159.222 "docker rm -f hand-gesture-container || true"

                        ssh -o StrictHostKeyChecking=no ec2-user@3.26.159.222 "docker run -d -p 80:80 --name hand-gesture-container hand-gesture-recognition:latest"
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                echo 'Verifying the deployed Docker container on EC2...'

                sshagent(['ec2-ssh-key']) {
                    bat '''
                        ssh -o StrictHostKeyChecking=no ec2-user@3.26.159.222 "docker ps --filter name=hand-gesture-container"
                    '''
                }
            }
        }
    }

    post {

        success {
            echo '=============================================='
            echo 'CI/CD PIPELINE COMPLETED SUCCESSFULLY!'
            echo 'Docker Desktop image transferred to EC2.'
            echo 'New container deployed successfully.'
            echo '=============================================='
        }

        failure {
            echo '=============================================='
            echo 'PIPELINE FAILED!'
            echo 'Check the Console Output.'
            echo '=============================================='
        }

        always {
            bat '''
                if exist hand-gesture-recognition.tar del /Q hand-gesture-recognition.tar
            '''
        }
    }
}
