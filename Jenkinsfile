pipeline {
    agent any

    environment {
        STUDENT_ID     = "FA23-BDS-044"
        IMAGE_NAME     = "ml-midterm-fa23-bds-044"
        CONTAINER_NAME = "ml-midterm-container"
        RECIPIENT      = "qasimalik@gmail.com"
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
                    pytest
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
                        -p 8000:8000 \
                        ${IMAGE_NAME}:latest
                    sleep 3
                    curl -f http://localhost:8000/health
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
                    to: "${env.RECIPIENT}",
                    subject: "Jenkins Pipeline ${currentBuild.currentResult} - ${env.STUDENT_ID} (${env.SHORT_SHA})",
                    body: """
                        <h3>Automated ML Retraining Pipeline Result</h3>
                        <p><b>Student Reg No:</b> ${env.STUDENT_ID}</p>
                        <p><b>Status:</b> ${currentBuild.currentResult}</p>
                        <p><b>Git SHA:</b> ${env.FULL_SHA}</p>
                        <p><b>Build URL:</b> ${env.BUILD_URL}</p>
                        <h4>/metrics Response:</h4>
                        <pre>${metricsOutput}</pre>
                    """,
                    mimeType: 'text/html'
                )
            }
        }
    }
}
