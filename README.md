# Jenkins CI CD pipeline for flask application

### Objective-1:
Set up a Jenkins pipeline that automates the testing and deployment of a simple Python web application.

1. Setup:
   - Install Jenkins on a virtual machine or use a cloud-based Jenkins service.
   - Configure Jenkins with Python and any necessary libraries.

I am using boto3 to create a EC2 machine on AWS and configuring it with java, jenkins, pip and streamlit.

```
#--------------------------Jenkins installation on EC2--------------------------------------------------------------
import boto3
ec2_client = boto3.client('ec2')

#configuring the webserver nginx
user_data_script = """#!/bin/bash
sudo apt-get -y update 
sudo apt-get -y upgrade 
sudo apt install -y openjdk-11-jdk 
java -version
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ >  /etc/apt/sources.list.d/jenkins.list'
sudo apt-get -y update 
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc   https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc]   https://pkg.jenkins.io/debian-stable binary/ | sudo tee   /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt install -y jenkins 
sudo apt update
sudo systemctl status Jenkins
sudo apt install -y python3-pip
sudo pip install streamlit
"""
#Define the parameters for your EC2 instance
instance_params = {
    'ImageId': 'ami-0287a05f0ef0e9d9a',
    'InstanceType': 't3.medium',
    'KeyName': 'adarsh_key',
    'MaxCount': 1,
    'MinCount': 1,
    'UserData': user_data_script,
}
#Launch the EC2 instance
instance = ec2_client.run_instances(**instance_params)
# Get the instance ID
instance_id = instance['Instances'][0]['InstanceId']
ec2_client.create_tags(Resources=[instance_id], Tags=[{'Key': 'Name', 'Value': 'adarsh-jenkins'}])
print(instance_id)
#-------------------------------------------------------------------------------------------------------------------
```

![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/2e78c90d-22fc-419a-b583-da215ad0253a)
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/740cbbba-e3c1-4275-bd1c-1de4846c6564)
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/00494b9b-977a-4b3b-ad9e-fdbe5ce84f32)

2. Source Code:
   - Fork the provided Python web application repository on GitHub (provide a link to a sample Python web application repository).
   - Clone the forked repository into your Jenkins server.

Lets create a new pipeline in the jenkins 
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/345ffc4a-cd68-449d-bd87-80b54917a69e)

Do install ssh plugin so that we can connect to our EC2 instance
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/0db7fe46-6bd3-4da9-bb3d-e4ade19868bb)

Configure ssh credientials. [ Dashboard > Manage Jenkins > Credentials > System > Global credentials]
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/3188ad22-98f5-448c-9458-325603d4f7e0)

```
#-------------------------Jenking File-------------------------------------
pipeline {
    agent any
    
    environment{
        EC2_HOST = 'ubuntu@13.127.200.219'
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
```
Application file are properly copied in the directory /home/ubuntu/
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/2c998bd4-3a36-4a47-b9eb-3cbefc1974cb)

![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/0be3ecbd-47e3-459a-ba07-b25e8b539ceb)


3. Jenkins Pipeline:
   - Create a Jenkins file in the root of your Python application repository.
   - Define a pipeline with the following stages:
     - Build: Install dependencies using pip.
     - Test: Run unit tests using a testing framework like pytest.
     - Deploy: If tests pass, deploy the application to a staging environment.

For installing packages we need to provide user jenkins with certain privileges.
```
sudo visudo
```
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/4109b04d-0756-4d05-ae72-5369c4e41de8)

use the below jenkins file to connect to the ec2 instance and deploy the application
```
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
```

4. Triggers:
   - Configure the pipeline to trigger a new build whenever changes are pushed to the main branch of the repository.

For triggering the new build whenever a new code is pushed in github - 

![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/9a517e9a-c014-4ab0-ab71-8de12594d2a9)

Go on the github repository's setting and webhook 
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/3d20f7ec-44a5-45fc-94ea-6705060dc35a)

5. Notifications:
   - Set up a notification system to alert via email when the build process fails or succeeds.

Install the email plugin
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/7d55a173-8d22-4ab7-bac5-ae9b8332a2cf)

Now we need to set up an SMTP server that can be used to send email notifications of build stages.
But for that, we need to do some setting -
 - first login into Gmail account
 - go to the security and 2-step verification
 - In the App passwords create a app with name "Jenkins"
 - Copy the app generated password that will be used to setup the SMTP server

![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/dc7b7211-be14-4197-841d-23fe4f52fbde)
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/e0d7dc95-97eb-4fab-8231-a1e64000842b)
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/9396bc2c-9414-4b3d-9564-f2230e223577)

Visit the Jenkins Dashboard [ Dashboard > Manage Jenkins > System > E-mail Notification ]
SMTP settings are : 
  - SMTP server : smtp.gmail.com
  - User Name : <use your gmail id>
  - Password : paste the app password which is copied from the gmail
  - Check the SSL box
  - SMTP Port - 465
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/7fdd720e-3ac3-4298-9c68-7a3fd57ce469)
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/817e1ab0-aa73-487c-ad44-6bf12e189f8f)

![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/0049fd5f-94ef-4db3-a6e6-4d171f5f5d0f)

We receive the email notification
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/b08ed72b-2b29-4f55-838a-b84d5db4277f)


Applications is up and running
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/5839db75-4433-4b3d-80fb-7b4db539c260)


### Objective-2: GitHub Actions CI/CD Pipeline Flask App

### Implement a CI/CD workflow using GitHub Actions for a Python application.

1. Setup:
   - Use a provided Python application repository on GitHub (provide a link to a sample Python application repository).
   - Ensure the repository has a main branch and a staging branch.
Github Repo: https://github.com/AdarshIITDH/jenkins_aws.git

![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/e34def44-04f8-451d-a5d9-1b0f966c1301)

2. GitHub Actions Workflow:
   - Create a .github/workflows directory in your repository.
   - Inside the directory, create a YAML file to define the workflow.

Go to Actions > create a new workflow as main.yml
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/a293fe65-11d1-4bf7-ae9e-7e0cf53bc1b3)

```
name: Ec2-deployment

on: 
  push:
    branches: 
      - main

jobs: 
  build:
    runs-on: ubuntu-latest
    
    steps: 
    - name: code checkout
      uses: actions/checkout@v2
      
    - name: install dependencies
      run: |
        sudo apt update
        sudo apt install python3-pip
        sudo pip install streamlit
        sudo pip install pytest
  test:
    runs-on: ubuntu-latest
    steps:     
    
    - name: code checkout
      uses: actions/checkout@v2
      
    - name: install dependencies
      run: |
        sudo apt update
        sudo apt install python3-pip
        sudo pip install streamlit
        sudo pip install pytest
        
    - name: build and test
      run: |
        # testing scripts
        pytest test_calculator.py
    
    - name: pushing code to staging
      run: |
        # testcases are passed pushing code to staging
        #git checkout staging
        
  deploy:
    runs-on: ubuntu-latest
    steps:         
    - name: deployment step
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ${{ secrets.EC2_USERNAME }}
        key: ${{ secrets.EC2_SSH_KEY }}
        port: ${{ secrets.PORT }}
        script: | 
          cd /home/ubuntu/
          git clone https://github.com/AdarshIITDH/jenkins_aws.git
          sudo apt install -y python3-pip
          sudo pip install streamlit 
          sudo streamlit run /home/ubuntu/jenkins_aws/calculator.py
```

3. Workflow Steps:
   - Define a workflow that performs the following jobs:
     - Install Dependencies: Install all necessary dependencies for the Python application using pip.
     - Run Tests: Execute the test suite using a framework like pytest.
     - Build: If tests pass, prepare the application for deployment.
     - Deploy to Staging: Deploy the application to a staging environment when changes are pushed to the staging branch.
     - Deploy to Production: Deploy the application to production when a release is tagged.

![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/38cf7ce2-20a1-4424-ac7b-972d218e36db)


4. Environment Secrets:
   - Use GitHub Secrets to store sensitive information required for deployments (e.g., deployment keys, API tokens).

![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/a4bff23c-68b3-4655-9242-10426d7bbbee)

Application is up and running
![image](https://github.com/AdarshIITDH/jenkins_aws/assets/60352729/3433b0fb-e28c-4799-9e38-ddc023ba57ac)






