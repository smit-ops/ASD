pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "smitn06/hand-gesture-recognition:latest"
    }

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
                echo 'Verifying Docker image...'

                bat '''
                    docker image inspect hand-gesture-recognition:latest
                '''
            }
        }

        stage('Docker Hub Login and Push') {
            steps {
                echo 'Logging into Docker Hub...'

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {

                    bat '''
                        echo %DOCKERHUB_TOKEN% | docker login -u %DOCKERHUB_USERNAME% --password-stdin

                        echo Tagging Docker image...
                        docker tag hand-gesture-recognition:latest %DOCKERHUB_USERNAME%/hand-gesture-recognition:latest

                        echo Pushing Docker image to Docker Hub...
                        docker push %DOCKERHUB_USERNAME%/hand-gesture-recognition:latest

                        echo Logging out from Docker Hub...
                        docker logout
                    '''
                }
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

        stage('Deploy to EC2') {
            steps {
                echo 'Pulling Docker image from Docker Hub and deploying to EC2...'

                sshagent(['ec2-ssh-key']) {
                    bat '''
                        echo Pulling latest Docker image...
                        ssh -o StrictHostKeyChecking=no ec2-user@3.26.159.222 "docker pull smitn06/hand-gesture-recognition:latest"

                        echo Removing old container...
                        ssh -o StrictHostKeyChecking=no ec2-user@3.26.159.222 "docker rm -f hand-gesture-container || true"

                        echo Starting new container...
                        ssh -o StrictHostKeyChecking=no ec2-user@3.26.159.222 "docker run -d -p 80:80 --name hand-gesture-container smitn06/hand-gesture-recognition:latest"
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                echo 'Verifying Docker container on EC2...'

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
            echo '=============================================='
            echo 'GitHub → Jenkins → Docker Build'
            echo '      → Docker Hub → AWS EC2'
            echo '=============================================='
            echo 'Docker image pushed successfully.'
            echo 'Docker container deployed successfully.'
            echo '=============================================='
        }

        failure {
            echo '=============================================='
            echo 'PIPELINE FAILED!'
            echo 'Check the Console Output.'
            echo '=============================================='
        }
    }
}
