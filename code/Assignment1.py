#!/usr/bin/env python3

#DevOps Assignment 1
#Mark Bates (20088639)
#Applied Computing (IoT)

import boto3
import sys

#creating instance with self assignmed key
def create_instance():
#	instance_tag = input("pleace provide an instance tag:\n")
	ec2 = boto3.resource("ec2")
	security_group = ec2.SecurityGroup("http")
	try:
		new_instance = ec2.create_instances(
			ImageId="ami-0d1bf5b68307103c2",
			MinCount=1,
			MaxCount=1,
			InstanceType="t2.nano",
			KeyName="mBatesKey",
			#SecurityGroupIds=["sg-94c11d2",], #was giving error
			TagSpecifications=[
				{
					"ResourceType": "instance",
					"Tags": [
						{
							"Key": "name",
							"Value": "Assign1"
						},
					]
				},
			],
			UserData="""#!/bin/bash
				yum install httpd -y
                		yum update httpd
                		systemctl enable httpd
                		systemctl start httpd
                		echo '<html>' > index.html
                		echo 'Private IP address: ' >> index.html
                		curl http://169.254.169.254/latest/meta-data/local-ipv4 >> index.html
				echo ' | Instance ID: ' >> index.html
                		curl http://169.254.169.254/latest/meta-data/instance-id >> index.html
                		echo " | Mac Address: " >> index.html
                		curl http://169.254.169.254/latest/meta-data/mac >> index.html
                		echo " | Subnet: " >> index.html
                		curl http://169.254.169.254/latest/meta-data/network/interfaces/macs/02:29:96:8f:>
                		cp index.html /var/www/html/index.html""",
		)
		print ("waiting for instance...")
        	time.sleep(12)
        	print ("almost there...")
		new_instance[0].wait_until_running()
		print ("instance is now up and running")
		print (new_instance[0].id)
		new_instance[0].reload()
		ip_address = new_instance[0].public_ip_address
        	print (ip_address)
        	try:
            		webbrowser.open("http://" + ip_address)
        	except Exception as error:
            		print (error)
	except Exception as error:
        print (error) #error exception to prevent code from crashing

def create_bucket():
	s3 = boto3.resource("s3")
	try:
		new_bucket = s3.create_bucket(
			ACL="public-read"
			Bucket="markbatesassignment1",
        		CreateBucketConfiguration={
            			"LocationConstraint": "eu-west-1"
        		},
		)
	except Exception as error:
		print(error)

create_instance()
create_bucket()
