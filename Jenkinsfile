pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        SONAR_TOKEN = credentials('SONAR_TOKEN')
    }

    stages {
        stage('Checkout') { steps { checkout scm } }

        stage('Unit Tests') {
            steps {
                sh 'pip install -r requirements-dev.txt'
                sh 'pytest tests/unit'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    withSonarQubeEnv('SonarQube-Server') {
                        sh "sonar-scanner -Dsonar.projectKey=ssp-product-service -Dsonar.sources=app -Dsonar.login=${SONAR_TOKEN}"
                    }
                }
            }
        }

        stage('Setup Terraform & Get ECR Repo') {
            steps {
                script {
                    dir('terraform') {
                        sh 'terraform init -backend-config="bucket=ssp-terraform-state-bucket" -backend-config="key=services/product-service/terraform.tfstate" -backend-config="region=${AWS_REGION}"'
                        sh 'terraform workspace select dev || terraform workspace new dev'
                        env.ECR_REPOSITORY_URL = sh(script: 'terraform output -raw ecr_repository_url', returnStdout: true).trim()
                    }
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                script {
                    def dockerImage = docker.build("ssp-product-service:${env.BUILD_NUMBER}", ".")
                    docker.withRegistry("https://${env.ECR_REPOSITORY_URL}", 'ecr:us-east-1') {
                        dockerImage.push("${env.BUILD_NUMBER}")
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Deploy to ECS') {
            steps {
                script {
                    dir('terraform') {
                        def imageUrl = "${env.ECR_REPOSITORY_URL}:${env.BUILD_NUMBER}"
                        sh "terraform apply -auto-approve -var=\"container_image=${imageUrl}\""
                    }
                }
            }
        }
    }
}
