pipeline {
    agent any

    environment {
        LOCAL_IMAGE = "hand-gesture-recognition:latest"
        GHCR_IMAGE  = "ghcr.io/smit-ops/hand-gesture-recognition:latest"
        EC2_HOST    = "3.26.159.222"
        EC2_USER    = "ec2-user"
    }

    stages {

        // =====================================================
        // 1. CHECKOUT
        // =====================================================
        stage('Checkout') {
            steps {
                echo '=========================================='
                echo 'CHECKING OUT PROJECT FROM GITHUB'
                echo '=========================================='

                checkout scm
            }
        }


        // =====================================================
        // 2. TEST
        // =====================================================
        stage('Test') {
            steps {
                echo '=========================================='
                echo 'RUNNING PROJECT TESTS'
                echo '=========================================='

                bat '''
                    if not exist index.html (
                        echo ERROR: index.html not found
                        exit /b 1
                    )

                    if not exist images (
                        echo ERROR: images folder not found
                        exit /b 1
                    )

                    if not exist real_fruits (
                        echo ERROR: real_fruits folder not found
                        exit /b 1
                    )

                    if not exist static (
                        echo ERROR: static folder not found
                        exit /b 1
                    )

                    if not exist Dockerfile (
                        echo ERROR: Dockerfile not found
                        exit /b 1
                    )

                    echo All required project files are present.
                    echo Test phase completed successfully!
                '''
            }
        }


        // =====================================================
        // 3. DOCKER BUILD
        // =====================================================
        stage('Docker Build') {
            steps {
                echo '=========================================='
                echo 'BUILDING DOCKER IMAGE'
                echo '=========================================='

                bat '''
                    docker build -t %LOCAL_IMAGE% .

                    if errorlevel 1 (
                        echo Docker build FAILED!
                        exit /b 1
                    )

                    echo Docker image built successfully!
                '''
            }
        }


        // =====================================================
        // 4. VERIFY DOCKER IMAGE
        // =====================================================
        stage('Verify Docker Image') {
            steps {
                echo '=========================================='
                echo 'VERIFYING DOCKER IMAGE'
                echo '=========================================='

                bat '''
                    docker image inspect %LOCAL_IMAGE%

                    if errorlevel 1 (
                        echo Docker image verification FAILED!
                        exit /b 1
                    )

                    echo Docker image verification successful!
                '''
            }
        }


        // =====================================================
        // 5. GHCR LOGIN + PUSH
        // =====================================================
        stage('GHCR Push') {
            steps {
                echo '=========================================='
                echo 'PUSHING IMAGE TO GITHUB CONTAINER REGISTRY'
                echo '=========================================='

                withCredentials([
                    usernamePassword(
                        credentialsId: 'ghcr-credentials',
                        usernameVariable: 'GHCR_USER',
                        passwordVariable: 'GHCR_TOKEN'
                    )
                ]) {

                    bat '''
                        echo Logging into GHCR...

                        echo %GHCR_TOKEN% | docker login ghcr.io -u %GHCR_USER% --password-stdin

                        if errorlevel 1 (
                            echo GHCR login FAILED!
                            exit /b 1
                        )

                        echo GHCR login successful!

                        echo Tagging Docker image...

                        docker tag %LOCAL_IMAGE% %GHCR_IMAGE%

                        if errorlevel 1 (
                            echo Docker tag FAILED!
                            docker logout ghcr.io
                            exit /b 1
                        )

                        echo Pushing Docker image to GHCR...

                        docker push %GHCR_IMAGE%

                        if errorlevel 1 (
                            echo GHCR push FAILED!
                            docker logout ghcr.io
                            exit /b 1
                        )

                        echo GHCR push successful!

                        docker logout ghcr.io
                    '''
                }
            }
        }


        // =====================================================
        // 6. TEST EC2 SSH
        // =====================================================
        stage('Test EC2 SSH') {
            steps {
                echo '=========================================='
                echo 'TESTING EC2 SSH CONNECTION'
                echo '=========================================='

                sshagent(['ec2-ssh-key']) {

                    bat '''
                        ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "echo EC2 SSH connection successful"

                        if errorlevel 1 (
                            echo EC2 SSH connection FAILED!
                            exit /b 1
                        )
                    '''
                }
            }
        }


        // =====================================================
        // 7. DEPLOY TO EC2
        // =====================================================
        stage('Deploy to EC2') {
            steps {
                echo '=========================================='
                echo 'DEPLOYING DOCKER IMAGE TO AWS EC2'
                echo '=========================================='

                sshagent(['ec2-ssh-key']) {

                    bat '''
                        echo Pulling latest image from GHCR...

                        ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "docker pull %GHCR_IMAGE%"

                        if errorlevel 1 (
                            echo Docker pull FAILED!
                            exit /b 1
                        )

                        echo Docker image pulled successfully!


                        echo Removing old container...

                        ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "docker rm -f hand-gesture-container 2>/dev/null || true"


                        echo Starting new container...

                        ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "docker run -d -p 80:80 --name hand-gesture-container %GHCR_IMAGE%"

                        if errorlevel 1 (
                            echo Docker container deployment FAILED!
                            exit /b 1
                        )

                        echo New Docker container started successfully!
                    '''
                }
            }
        }


        // =====================================================
        // 8. VERIFY DEPLOYMENT
        // =====================================================
        stage('Verify Deployment') {
            steps {
                echo '=========================================='
                echo 'VERIFYING EC2 DEPLOYMENT'
                echo '=========================================='

                sshagent(['ec2-ssh-key']) {

                    bat '''
                        ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "docker ps --filter name=hand-gesture-container"

                        if errorlevel 1 (
                            echo Deployment verification FAILED!
                            exit /b 1
                        )

                        echo Deployment verification successful!
                    '''
                }
            }
        }
    }


    // =========================================================
    // POST ACTIONS
    // =========================================================
    post {

        success {
            echo '=================================================='
            echo '       CI/CD PIPELINE COMPLETED SUCCESSFULLY'
            echo '=================================================='
            echo ''
            echo 'GitHub'
            echo '   ↓'
            echo 'GitHub Webhook'
            echo '   ↓'
            echo 'Jenkins'
            echo '   ↓'
            echo 'Test'
            echo '   ↓'
            echo 'Docker Build'
            echo '   ↓'
            echo 'GHCR Push'
            echo '   ↓'
            echo 'AWS EC2'
            echo '   ↓'
            echo 'Docker Pull'
            echo '   ↓'
            echo 'Docker Run'
            echo ''
            echo '=================================================='
            echo 'Application deployed successfully!'
            echo '=================================================='
        }

        failure {
            echo '=================================================='
            echo '             PIPELINE FAILED'
            echo '=================================================='
            echo 'Check the Console Output for the failed stage.'
            echo '=================================================='
        }
    }
}
