pipeline {
    agent any 

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'  
        DOCKER_IMAGE = 'cithit/dayam7'                                   //<-----change this to your MiamiID!
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/miamioh-dayam7/225-lab5-1.git'     //<-----change this to match this new repository!
        KUBECONFIG = credentials('dayam7-225')                           //<-----change this to match your kubernetes credentials (MiamiID-225)! 
    }

    stages {
        stage('Code Checkout') {
            steps {
                try {
                    cleanWs()
                    checkout([$class: 'GitSCM', branches: [[name: '*/main']],
                              userRemoteConfigs: [[url: "${GITHUB_URL}"]]])
                } catch (Exception e) {
                    currentBuild.result = 'FAILURE'
                    error("Failed to checkout code: ${e.message}")
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                try {
                    script {
                        docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}", "-f Dockerfile.build .")
                    }
                } catch (Exception e) {
                    currentBuild.result = 'FAILURE'
                    error("Failed to build Docker image: ${e.message}")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                try {
                    script {
                        docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_CREDENTIALS_ID}") {
                            docker.image("${DOCKER_IMAGE}:${IMAGE_TAG}").push()
                        }
                    }
                } catch (Exception e) {
                    currentBuild.result = 'FAILURE'
                    error("Failed to push Docker image: ${e.message}")
                }
            }
        }

        stage('Deploy to Dev Environment') {
            steps {
                try {
                    script {
                        // This sets up the Kubernetes configuration using the specified KUBECONFIG
                        def kubeConfig = readFile(KUBECONFIG)
                        // This updates the deployment-dev.yaml to use the new image tag
                        sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-dev.yaml"
                        sh "kubectl apply -f deployment-dev.yaml"
                    }
                } catch (Exception e) {
                    currentBuild.result = 'FAILURE'
                    error("Failed to deploy to Dev environment: ${e.message}")
                }
            }
        }

        stage('Generate Test Data') {
            steps {
                try {
                    script {
                        // Ensure the label accurately targets the correct pods.
                        def appPod = sh(script: "kubectl get pods -l app=flask -o jsonpath='{.items[0].metadata.name}'", returnStdout: true).trim()
                        // Execute command within the pod. 
                        sh "kubectl get pods"
                        sh "sleep 5"
                        sh "kubectl exec ${appPod} -- python3 data-gen.py"
                    }
                } catch (Exception e) {
                    currentBuild.result = 'FAILURE'
                    error("Failed to generate test data: ${e.message}")
                }
            }
        }

        // Remaining stages with similar error handling...
        
        // Run Acceptance Tests, Remove Test Data, Check Kubernetes Cluster, etc.

    }

    post {
        success {
            slackSend color: "good", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        unstable {
            slackSend color: "warning", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        failure {
            slackSend color: "danger", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
    }
}

