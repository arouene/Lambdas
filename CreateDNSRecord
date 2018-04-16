# Create a DNS record for EC2 Instances

import os
import boto3


HOSTED_ZONE_ID = os.environ['HOSTED_ZONE_ID']
DOMAIN_NAME = os.environ['DOMAIN_NAME']


def lambda_handler(event, context):
    InstanceId = event['detail']['instance-id']
    State = event['detail']['state']
    Region = event['region']

    if State != "running":
        return

    # Setup Boto3 client
    boto3.setup_default_session(region_name=Region)
    ec2 = boto3.client("ec2")
    dns = boto3.client("route53")

    # Get instance's name
    instance = ec2.describe_instances(InstanceIds=[InstanceId])
    tags = instance['Reservations'][0]['Instances'][0]['Tags']
    name = list(filter(lambda x: x['Key'] == 'Name', tags))[0]['Value']
    new_ip = instance['Reservations'][0]['Instances'][0]['PrivateIpAddress']

    # Change / Create DNS Record
    dns.change_resource_record_sets(
        HostedZoneId=HOSTED_ZONE_ID,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': name + DOMAIN_NAME,
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [
                            {
                                'Value': new_ip
                            },
                        ]
                    }
                }
            ]
        })
