#!/usr/bin/env python3

#DevOps Assignment 1
#Mark Bates (20088639)
#Applied Computing (IoT)

import boto3
import sys
import subprocess
import webbrowser

print ("""====================================================
DEVOPS ASSIGNMENT 1 | MARK BATES | APPLIED COMPUTING
====================================================""")

#================================ INSTANCE CODE ================================
def create_instance():
	ec2 = boto3.resource("ec2")
	ec2b = boto3.client("ec2")
	security_group = ec2.SecurityGroup("http")

	print ("creating new instance...")

	try:
		print ("configuring instance settings")
		new_instance = ec2.create_instances(
			ImageId="ami-0d1bf5b68307103c2",
			MinCount=1,
			MaxCount=1,
			InstanceType="t2.nano",
			KeyName="mBatesKey",
			SecurityGroupIds=["sg-0848edc382b3f0fbd",], #security groups that enables http and TCP
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
				""", #User Data that runs an apache website and replaces the default webpage to display meta data
		)

		print ("waiting for instance...")
		new_instance[0].wait_until_running() #wait for the instance to run before displaying in terminal
		print ("instance running")
		print ("instance ID: " + new_instance[0].id)

		print ("reloading instance to display ip address")
		new_instance[0].reload() #reload instance to get ip address to display on the console
		ip_address = new_instance[0].public_ip_address
		print ("public ip address: " + ip_address)

		print ("waiting for status checks...")

		waiter = ec2b.get_waiter("instance_status_ok") #waiter to halt program until the instance passes all status checks and is ready to run

		waiter.wait(
			InstanceIds=[
				new_instance[0].id,
			],
			WaiterConfig={ #waiter will check instance status every 15 seconds until status is confirmed to be ok
				"Delay": 15,
				"MaxAttempts": 100 #waiter will check 100 times before crashing
			}
		)

		print ("spinning up webpage")

		try:
			webbrowser.open("http://" + ip_address + "/") #import to open up instance in a web browser
		except Exception as error:
			print (error)
			print ("failed to load to webpage. Instance likely does not have the propper security settings or is still pending checks")
	except Exception as error:
		print (error)

#	try:
#		subprocess.run(["scp -i mBatesKey.pem moniter.sh ec2-user@{ip_address}:."], shell=True)
#		subprocess.run(["sudo ssh -i mBatesKey.pem ec2-user@{ip_address} 'chmod 700 moniter.sh'"], shell=True)
#		subprocess.run(["sudo ssh -i mBatesKey.pem ec2-user@{ip_address} ./moniter.sh"], shell=True)
#	except Exception as error:
#		print (error)

create_instance()

#================================ BUCKET CODE ================================

def create_bucket():
	s3 = boto3.resource("s3")
	s3b = boto3.client("s3")

	print ("====================================================")

	try:
		print ("configuring bucket settings")
		new_bucket = s3.create_bucket(
			ACL="public-read", #allowing users to read the bucket
			Bucket="markbatesassignment1",
			CreateBucketConfiguration={
				"LocationConstraint": "eu-west-1"
			},
		)
	except Exception as error:
		print (error)
		print ("s3 buckets each have their own unique name, no two can be the same. Be sure that the bucket that is created has a unique and unused name")
		print ("make sure that the s3 bucket is configured to the appropriate location")

	try:
		print ("grabbing image URL")
		subprocess.run("curl http://devops.witdemo.net/assign1.jpg -o image.jpeg", shell=True) #cur command to grab the image at the URL destination
		print ("uploading image to bucket")
		s3.meta.client.upload_file("/mnt/c/Users/markb/OneDrive/Desktop/Year3/Semester1/DevOps/image.jpeg", "markbatesassignment1", "image.jpeg") #uploading image to assigned bucket
	except Exception as error:
		print (error)
		print ("failure to get and upload image. Either the webpage or the destination directory is not correct")

	print ("creating index.html file")
	file = open("index.html", "w") #creating an index.html file to display the image
	message = """<!DOCTYPE html>
		<html><img src="image.jpeg"></html>"""
	file.write(message)
	file.close()

	try:
		print ("uploading index.html to bucket")
		s3.meta.client.upload_file("/mnt/c/Users/markb/OneDrive/Desktop/Year3/Semester1/DevOps/index.html", "markbatesassignment1", "index.html")
	except Exception as error:
		print (error)
		print ("failure to upload file. the path to the directory may be incorrect, or the file does not exist")

	print ("making files public")
	makeimagepublic = s3b.put_object_acl( #setting the files to public read so they can be visible on the webpage
		ACL="public-read",
		Bucket="markbatesassignment1",
		Key="image.jpeg"
		)

	makeindexpublic = s3b.put_object_acl(
		ACL="public-read",
		Bucket="markbatesassignment1",
		Key="index.html"
		)

	print ("all files public!")

	try:
		print ("configuring bucket website")
		websiteconfig = s3b.put_bucket_website( #configuring the bucket to a website and setting it's index to index.html
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

create_bucket()
