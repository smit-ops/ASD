pipeline {
    agent any

    stages {

        stage('Test GHCR Login') {
            steps {

                echo 'Testing GitHub Container Registry authentication...'

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

                        echo GHCR login SUCCESSFUL!

                        docker logout ghcr.io
                    '''
                }
            }
        }
    }
}
