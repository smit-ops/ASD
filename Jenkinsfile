pipeline {
    agent any

    stages {

        stage('Test Docker Hub Login') {
            steps {

                echo 'Testing Docker Hub authentication...'

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-final',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_TOKEN'
                    )
                ]) {

                    bat '''
                        echo %DOCKER_TOKEN% | docker login -u %DOCKER_USER% --password-stdin

                        if errorlevel 1 (
                            echo Docker Hub login FAILED!
                            exit /b 1
                        )

                        echo Docker Hub login SUCCESSFUL!

                        docker logout
                    '''
                }
            }
        }
    }
}
