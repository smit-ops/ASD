pipeline {
    agent any

    stages {

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

    }
}
