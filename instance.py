#--------------------------Jenkins installation on EC2-------------
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
sudo systemctl status jenkins
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
#-------------------------------------------------------------------------------

