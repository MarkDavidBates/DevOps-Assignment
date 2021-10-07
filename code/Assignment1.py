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
			]
		)
		new_instance[0].wait_until_running()
		print ("instance is now up and running")
		print (new_instance[0].id)
	except Exception as error:
		print (error)

create_instance()
