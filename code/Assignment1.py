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
			UserData="""
                		#!/bin/bash
                		echo '<html>' > index.html
                		echo 'Private IP address: ' >> index.html
                		curl http://169.254.169.254/latest/meta-data/local-ipv4 >> index.html
                		cp index.html /var/www/html/index.html""",
		)
		new_instance[0].wait_until_running()
		print ("instance is now up and running")
		print (new_instance[0].id)
		print (new_instance[0].public_ip_address)
	except Exception as error:
		print (error)

def create_bucket():
	new_bucket = s3.create_bucket(
		ACL="public-read-write"
		Bucket="MarkBatesAssignment1",
        	CreateBucketConfiguration={
            		"LocationConstraint": "eu-west-1"
        	},
        	ObjectlockEnablesForBucket=True
)

create_instance()
