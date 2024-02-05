pipeline {
    agent any

    environment {
        PATH = "/usr/local/bin:${env.PATH}"
    }

    stages {
        stage('Setup Environment') {
            steps {
                script {
                    // Define Docker tool installation
                    def dockerTool = tool 'Docker'
                    
                    // Run the entire stage inside a Docker container
                    withDockerContainer(image: 'amazonlinux:2', tool: dockerTool) {
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
                script {
                    // Define Docker tool installation
                    def dockerTool = tool 'Docker'
                    
                    // Run the Python script inside a Docker container
                    withDockerContainer(image: 'amazonlinux:2', tool: dockerTool) {
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
}
