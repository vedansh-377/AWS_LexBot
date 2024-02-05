pipeline {
    agent any

    environment {
        PATH = "/usr/local/bin:${env.PATH}"
    }

    stages {
        stage('Setup Environment') {
            steps {
                // Run the entire pipeline in a Docker container
                script {
                    docker.image('amazonlinux:2').inside {
                        // Update the package list and install Python3
                        sh 'yum update -y && yum install -y python3'

                        // Install pip and required Python packages
                        sh 'yum install -y python3-pip'
                        sh 'pip3 install boto3 requests'
                    }
                }
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
                        docker.image('amazonlinux:2').inside {
                            sh 'python3 Export.py'
                        }
                    }
                }
            }
        }
    }
}
