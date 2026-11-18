```groovy
pipeline {
    agent any

    environment {
        STUDENT_ID     = "FA23-BDS-044"
        IMAGE_NAME     = "wasiahmed1905/devops-labmid"
        CONTAINER_NAME = "ml-midterm-container"
        SENDER_EMAIL   = "wasiahmed1905@gmail.com"
    }

    stages {

        stage('Checkout Latest Code & Data') {
            steps {
                checkout scm

                script {
                    env.FULL_SHA = sh(
                        script: "git rev-parse HEAD",
                        returnStdout: true
                    ).trim()

                    env.SHORT_SHA = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()

                    // Get latest commit author's name
                    def rawAuthor = sh(
                        script: "git log -1 --pretty=format:'%an'",
                        returnStdout: true
                    ).trim()

                    // Get latest commit author's email
                    def rawEmail = sh(
                        script: "git log -1 --pretty=format:'%ae'",
                        returnStdout: true
                    ).trim()

                    // Validate commit author's email
                    if (!rawEmail ||
                        !(rawEmail ==~ /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$/) ||
                        rawEmail.toLowerCase().contains("noreply.github.com")) {

                        error(
                            "Valid commit author email not found. " +
                            "Configure Git user.email with a deliverable email address."
                        )
                    }

                    env.COMMIT_AUTHOR = rawAuthor
                    env.COMMIT_EMAIL = rawEmail

                    echo "Commit: ${env.FULL_SHA}"
                    echo "Commit Author: ${env.COMMIT_AUTHOR}"
                    echo "Notification Recipient: ${env.COMMIT_EMAIL}"
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
                    docker build \
                        --build-arg GIT_COMMIT=${FULL_SHA} \
                        -t ${IMAGE_NAME}:latest \
                        -t ${IMAGE_NAME}:${SHORT_SHA} \
                        .
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

                    echo "Waiting for application to become ready..."

                    for i in $(seq 1 10); do
                        if curl -fsS http://localhost:8000/health; then
                            echo "Health check passed!"
                            break
                        fi

                        if [ "$i" -eq 10 ]; then
                            echo "Health check failed!"
                            docker logs ${CONTAINER_NAME}
                            exit 1
                        fi

                        sleep 3
                    done

                    echo "Checking application metrics..."

                    curl -fsS http://localhost:8000/metrics

                    echo "Deployment completed successfully."
                '''
            }
        }
    }

    post {
        always {
            script {
                def ec2Ip = sh(
                    script: "curl -fsS http://checkip.amazonaws.com || echo '13.51.240.196'",
                    returnStdout: true
                ).trim()

                def metricsOutput = sh(
                    script: "curl -fsS http://localhost:8000/metrics || echo 'Metrics unavailable'",
                    returnStdout: true
                ).trim()

                // Send report ONLY to the latest commit author
                def recipients = env.COMMIT_EMAIL

                if (recipients) {
                    try {
                        emailext(
                            from: "${env.SENDER_EMAIL}",
                            to: "${recipients}",
                            subject: "Jenkins Build ${currentBuild.currentResult} - ${env.STUDENT_ID} (${env.SHORT_SHA ?: 'N/A'})",
                            body: """
                                <h3>Automated ML Retraining Pipeline Report</h3>

                                <p><b>Student Reg No:</b> ${env.STUDENT_ID}</p>

                                <p><b>Commit Author:</b> ${env.COMMIT_AUTHOR ?: 'Unavailable'}</p>

                                <p><b>Commit Author Email:</b> ${env.COMMIT_EMAIL ?: 'Unavailable'}</p>

                                <p><b>Build Status:</b> ${currentBuild.currentResult}</p>

                                <p><b>Git Commit SHA:</b> ${env.FULL_SHA ?: 'Unavailable'}</p>

                                <p><b>Live Metrics URL:</b>
                                <a href="http://${ec2Ip}:8000/metrics">
                                http://${ec2Ip}:8000/metrics
                                </a></p>

                                <p><b>Jenkins Build URL:</b> ${env.BUILD_URL}</p>

                                <h4>Live Metrics Output:</h4>
                                <pre>${metricsOutput}</pre>
                            """,
                            mimeType: 'text/html'
                        )

                        echo "Build report sent to: ${recipients}"

                    } catch (Exception e) {
                        echo "WARNING: Email notification failed: ${e.getMessage()}"
                        echo "Check Jenkins SMTP configuration."
                    }
                } else {
                    echo "WARNING: No commit author email available. Report not sent."
                }
            }
        }
    }
}
```
