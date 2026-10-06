pipeline {
    agent any

    environment {
        GHCR_IMAGE = "ghcr.io/smit-ops/hand-gesture-recognition:latest"
        LOCAL_IMAGE = "hand-gesture-recognition:latest"
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
                echo 'Testing required project files...'

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

                bat '''
                    docker build -t %LOCAL_IMAGE% .
                '''
            }
        }

        stage('Verify Docker Image') {
            steps {
                echo 'Verifying Docker image...'

                bat '''
                    docker image inspect %LOCAL_IMAGE%
                '''
            }
        }

        stage('GHCR Login and Push') {
            steps {
                echo 'Logging into GitHub Container Registry...'

                withCredentials([
                    usernamePassword(
                        credentialsId: 'ghcr-credentials',
                        usernameVariable: 'GHCR_USER',
                        passwordVariable: 'GHCR_TOKEN'
                    )
                ]) {

                    bat '''
                        echo %GHCR_TOKEN% | docker login ghcr.io -u %GHCR_USER% --password-stdin

                        if errorlevel 1 (
                            echo GHCR login FAILED!
                            exit /b 1
                        )

                        echo GHCR login successful!

                        echo Tagging image...
                        docker tag %LOCAL_IMAGE% %GHCR_IMAGE%

                        if errorlevel 1 (
                            echo Docker tag FAILED!
                            exit /b 1
                        )

                        echo Pushing image to GHCR...
                        docker push %GHCR_IMAGE%

                        if errorlevel 1 (
                            echo GHCR push FAILED!
                            exit /b 1
                        )

                        echo ==========================================
                        echo GHCR PUSH SUCCESSFUL!
                        echo ==========================================

                        docker logout ghcr.io
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '=========================================='
            echo 'DOCKER IMAGE PUSHED TO GHCR SUCCESSFULLY!'
            echo '=========================================='
            echo 'Image: ghcr.io/smit-ops/hand-gesture-recognition:latest'
            echo '=========================================='
        }

        failure {
            echo '=========================================='
            echo 'PIPELINE FAILED!'
            echo 'Check the Console Output.'
            echo '=========================================='
        }
    }
}
