pipeline {
    agent any
    stages {
        stage('Lint') {
            steps {
                sh 'sudo pip3.8 install flake8'
                sh '/usr/local/bin/python3.8 -m flake8 --statistics'
            }
        }
        stage('Generate Docs') {
            steps {
                sh 'chmod -R 755 .'
            /**
                sh 'sudo pip3.8 install jinja2 requests'
                sh '/usr/local/bin/python3.8 ./create_docs.py'

            **/
            }
        }
        stage('Commit Docs') {
            steps {
                echo 'Commit Docs'
                sh 'git branch'
                /**
                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'github-user', usernameVariable: 'GIT_AUTHOR_NAME', passwordVariable: 'GIT_PASSWORD']]) {
                    sh "git commit -a -m 'Documentation Update for Commit $GIT_COMMIT'"
                    sh('git push origin $BRANCH_NAME https://${GIT_AUTHOR_NAME}:${GIT_PASSWORD}@github.com/trinity-team/rubrik-sdk-for-python.git --tags -f --no-verify')
                }
                **/
            }
        }
        stage('Function Tests') {
            steps {
                echo 'Run Tests'
                withCredentials([
                    usernamePassword(credentialsId: 'polaris_beta', usernameVariable: 'POLARIS_BETA_USR', passwordVariable: 'POLARIS_BETA_PWD'),
                    usernamePassword(credentialsId: 'polaris_prod', usernameVariable: 'POLARIS_PROD_USR', passwordVariable: 'POLARIS_PROD_PWD')
                ]) {
                    sh 'printenv'
                }
            }
        }
        stage('Coverage') {
            steps {
                sh 'pip3.8 install pytest-cov'
                sh 'pytest -v --cov'
            }
        }
    }
    post {
        always {
            cleanWs()
        }
        success {
            echo 'successful'
        }
        failure {
            echo 'failed'
        }
        unstable {
            echo 'unstable'
        }
        changed {
            echo 'changed'
        }
    }
}

