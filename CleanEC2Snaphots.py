import os
import boto3
from datetime import datetime, timedelta

# Environment variable, number of days to keep
RETENTION_DELTA = os.environ['RETENTION_DELTA']

def lambda_handler(event, context):
    boto3.setup_default_session(region_name=event['region'])
    ec2 = boto3.client("ec2")
    
    retention_date = datetime.utcnow() - timedelta(days=RETENTION_DELTA)
    
    # Get snapshots list
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])
    for i in snapshots['Snapshots']:
        start_date = i['StartTime'].replace(tzinfo=None)
        if start_date < retention_date:
            # delete snapshot
            print("Deleting: {} ({})".format(i['SnapshotId'], start_date.strftime('%c')))
            ec2.delete_snapshot(SnapshotId=i['SnapshotId'])
