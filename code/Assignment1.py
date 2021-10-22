#!/usr/bin/env python3

#DevOps Assignment 1
#Mark Bates (20088639)
#Applied Computing (IoT)

import boto3
import sys
import subprocess
import time
import webbrowser

#creating instance that will display metadata on the webpage
#instance is created with the appropriate Security Group, instance Type, etc
#UserData allows the code to startup and run a website that will display the instance metadata
def create_instance():
	ec2 = boto3.resource("ec2")
	ec2b = boto3.client("ec2")
	security_group = ec2.SecurityGroup("http")
	try:
		new_instance = ec2.create_instances(
			ImageId="ami-0d1bf5b68307103c2",
			MinCount=1,
			MaxCount=1,
			InstanceType="t2.nano",
			KeyName="mBatesKey",
			SecurityGroupIds=["sg-0848edc382b3f0fbd",],
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
				curl http://169.254.169.254/latest/meta-data/network/interfaces/macs/02:29:96:8f:6a:2d/subnet-id
				cp index.html /var/www/html/index.html
				""",
		)

		print ("waiting for instance...")
		time.sleep(12)
		print ("almost there...")
		new_instance[0].wait_until_running() #wait for the instance to run before displaying in terminal
		print ("instance is now up and running :)")
		print ("instance ID: " + new_instance[0].id)

		new_instance[0].reload()
		ip_address = new_instance[0].public_ip_address
		print ("public ip address: " + ip_address)

		print ("spinning up webpage...")

		waiter = ec2b.get_waiter("instance_status_ok")
		try:
			webbrowser.open("http://" + ip_address + "/")
		except Exception as error:
			print (error)
	except Exception as error:
		print (error) #error exception to prevent code from crashing

def create_bucket():
	s3 = boto3.resource("s3")
	s3b = boto3.client("s3")
	try:
		new_bucket = s3.create_bucket(
			ACL="public-read",
			Bucket="markbatesassignment1",
			CreateBucketConfiguration={
				"LocationConstraint": "eu-west-1"
			},
		)
	except Exception as error:
		print (error)

	try:
		subprocess.run("curl http://devops.witdemo.net/assign1.jpg -o image.jpeg", shell=True)
		s3.meta.client.upload_file("/mnt/c/Users/markb/OneDrive/Desktop/Year3/Semester1/DevOps/image.jpeg", "markbatesassignment1", "image.jpeg")
	except Exception as error:
		print (error)

	f = open("index.html", "w")
	message = """<!DOCTYPE html>
		<html><img src="image.jpeg"></html>"""
	f.write(message)
	f.close()

	try:
		s3.meta.client.upload_file("/mnt/c/Users/markb/OneDrive/Desktop/Year3/Semester1/DevOps/index.html", "markbatesassignment1", "index.html")
	except Exception as error:
		print (error)

	makeimagepublic = s3b.put_object_acl(
		ACL="public-read",
		Bucket="markbatesassignment1",
		Key="image.jpeg"
		)

	makeindexpublic = s3b.put_object_acl(
		ACL="public-read",
		Bucket="markbatesassignment1",
		Key="index.html"
		)

	print ("all files public")

	try:
		websiteconfig = s3b.put_bucket_website(
			Bucket="markbatesassignment1",
			WebsiteConfiguration={
				"IndexDocument": {
					"Suffix": "index.html"
				},
			},
			)
		print ("website configured")
	except Exception as error:
		print (error)

	try:
		webbrowser.open("https://markbatesassignment1.s3.eu-west-1.amazonaws.com/index.html")
		print ("opening URL in browser")
	except Exception as error:
		print (error)

create_instance()
create_bucket()
