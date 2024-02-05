pipeline {
    agent any

    stages {
        stage('Setup Environment') {
            steps {
                // Install Python and any required dependencies
                sh 'apt-get update && apt-get install -y python3'
                sh 'pip install boto3 requests'
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
                        sh 'python lambda.py'
                    }
                }
            }
        }
    }
}
