pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh 'echo "Testing application..."'
            }
        }

        stage('Build') {
            steps {
                sh 'echo "Building application..."'
            }
        }
    }
}