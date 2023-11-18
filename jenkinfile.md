#-------------------------Copying repo in ec2------------------------------------
pipeline {
    agent any
    environment{
        EC2_HOST = 'ubuntu@13.234.75.100'
        REMOTE_DIR = '/home/ubuntu'
    }

    stages {
        stage('Cloning the git repo') {
            steps {
                // Cloning the GitHub repository into the Jenkins workspace
                git url: 'https://github.com/AdarshIITDH/jenkins_aws.git', branch: 'main'
            }
        }
        stage('Coping web application to EC2'){
            steps{
                echo 'Deploying into the ec2'
                sh "echo 'workspace directory is ${WORKSPACE}'"
                sh "ls ${WORKSPACE}"
                sh "pwd"
                sshagent(['aws-ec2-cred']){
                    sh "scp -o StrictHostKeyChecking=no ${WORKSPACE}/* ${EC2_HOST}:${REMOTE_DIR}"
                }
            }
        }
        stage('Build') {
            steps {
                // Install dependencies using pip
                sshagent(['aws-ec2-cred']){
                    sh 'sudo apt install -y python3-pip'
                    sh 'sudo pip install streamlit'
                    sh 'sudo pip install pytest'
                    mail bcc: '', body: 'hello build is sucessfull', cc: '', from: '', replyTo: '', subject: 'email form jenkins', to: 'adarsh307kumar@gmail.com'
                }
            }
        }
        stage('Test') {
            steps{
                sh 'sudo pytest /home/ubuntu/test_calculator.py'
                mail bcc: '', body: 'hello Testing is sucessfull', cc: '', from: '', replyTo: '', subject: 'email form jenkins', to: 'adarsh307kumar@gmail.com'
                }
        }
        stage('Deploy') {
            when {
                expression {
                    // Check if the previous stage (Test) was successful
                    currentBuild.resultIsBetterOrEqualTo('SUCCESS')
                }
            }
            steps {
                sh 'sudo streamlit run /home/ubuntu/calculator.py'
            }
        }
        
        // stage('email') {
        //     steps {
        //         mail bcc: '', body: 'hello build is sucessfull', cc: '', from: '', replyTo: '', subject: 'email form jenkins', to: 'adarsh307kumar@gmail.com'
        //     }
        // }
    
    }
    post{
        success{
            echo 'cloning successfully completed'
        }
        failure{
            echo 'Cloning failed'
        }
    }
}
#-------------------------------------------------------------










