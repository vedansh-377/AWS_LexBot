pipeline {
    agent any

    environment {
        PATH = "/usr/local/bin:${env.PATH}"
    }

    stages {
        stage('Setup Environment') {
            steps {
                // Make sure Jenkins has the necessary permissions for apt-get
                sh 'sudo apt-get update && sudo apt-get install -y python3'

                // Install pip and required Python packages
                sh 'sudo apt-get install -y python3-pip'
                sh 'pip3 install boto3 requests'
            }
        }

        stage('Run Python Script') {
            steps {
                // Execute the Python script with AWS credentials
                script {
                    withCredentials([[
                        $class: 'AmazonWebServicesCredentialsBinding',
                        accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                        secretKeyVariable: 'AWS_SECRET_ACCESS_KEY',
                        credentialsId: 'your-aws-credentials-id'
                    ]]) {
                        sh 'python3 lambda.py'
                    }
                }
            }
        }
    }
}
