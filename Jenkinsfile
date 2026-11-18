pipeline {
    agent any

    environment {
        STUDENT_ID     = "FA23-BDS-044"
        IMAGE_NAME     = "ml-midterm-fa23-bds-044"
        CONTAINER_NAME = "ml-midterm-container"
        RECIPIENT      = "qasimalik@gmail.com"
        SENDER_EMAIL   = "wasiahmed1905@gmail.com>"
        EC2_PUBLIC_IP  = "13.51.240.196"
    }

    stages {
        stage('Checkout Latest Code & Data') {
            steps {
                checkout scm
                script {
                    env.FULL_SHA  = sh(script: "git rev-parse HEAD", returnStdout: true).trim()
                    env.SHORT_SHA = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                }
            }
        }

        stage('Install Dependencies & Train Model') {
            steps {
                sh '''
                    rm -rf venv
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    GIT_COMMIT=${FULL_SHA} python3 train.py
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${SHORT_SHA} -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('Deploy on AWS EC2') {
            steps {
                sh '''
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        --restart unless-stopped \
                        -p 0.0.0.0:8000:8000 \
                        ${IMAGE_NAME}:latest
                    curl --retry 5 --retry-delay 2 --retry-connrefused -f http://localhost:8000/health
                    curl -f http://localhost:8000/metrics
                '''
            }
        }
    }

    post {
        always {
            script {
                def metricsOutput = sh(script: "curl -s http://localhost:8000/metrics || echo 'Metrics unavailable'", returnStdout: true).trim()
                emailext(
                    from: "${env.SENDER_EMAIL}",
                    to: "${env.RECIPIENT}",
                    subject: "Jenkins Build ${currentBuild.currentResult} - ${env.STUDENT_ID} (${env.SHORT_SHA})",
                    body: """
                        <h3>Automated ML Retraining Pipeline Report</h3>
                        <p><b>Student Reg No:</b> ${env.STUDENT_ID}</p>
                        <p><b>Build Status:</b> ${currentBuild.currentResult}</p>
                        <p><b>Git Commit SHA:</b> ${env.FULL_SHA}</p>
                        <p><b>Live Metrics URL:</b> <a href="http://${env.EC2_PUBLIC_IP}:8000/metrics">http://${env.EC2_PUBLIC_IP}:8000/metrics</a></p>
                        <p><b>Jenkins Build URL:</b> ${env.BUILD_URL}</p>
                        <h4>Live /metrics Output:</h4>
                        <pre>${metricsOutput}</pre>
                    """,
                    mimeType: 'text/html'
                )
            }
        }
    }
}
