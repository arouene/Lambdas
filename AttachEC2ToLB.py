import os
import boto3


# Environment variables
node_prefix = os.environ['NODE_PREFIX']
lb_node_http_arn = os.environ['LB_NODE_HTTP_ARN']
lb_node_https_arn = os.environ['LB_NODE_HTTPS_ARN']


class ELB():
    def __init__(self):
        self.__elb = boto3.client("elbv2")

    def _is_in_targets(self, Id, arn):
        targets = self.__elb.describe_target_health(TargetGroupArn=arn)
        for i in targets['TargetHealthDescriptions']:
            if i['Target']['Id'] == Id:
                return True
        return False
    
    def register_target(self, Id, arn):
        if not self._is_in_targets(Id, arn):
            self.__elb.register_targets(
                TargetGroupArn = arn,
                Targets = [{'Id': Id}]
            )
            return True
        return False


def lambda_handler(event, context):
    InstanceId = event['detail']['instance-id']
    State = event['detail']['state']
    Region = event['region']

    if State != "running":
        return
    
    # Setup Boto3 client
    boto3.setup_default_session(region_name=Region)
    ec2 = boto3.client("ec2")
    elb = ELB()
    
    # Get instance's name
    instance = ec2.describe_instances(InstanceIds=[InstanceId])
    tags = instance['Reservations'][0]['Instances'][0]['Tags']
    name = list(filter(lambda x: x['Key'] == 'Name', tags))[0]['Value']
    
    # If it's "that type" of instance (match prefix)
    if node_prefix in name:
        # Add to the LBNodesHTTP targets
        if elb.register_target(InstanceId, lb_node_http_arn):
            print("Instance {} append to target group LBNodesHTTP".format(name))
        else:
            print("Instance {} already in target group LBNodesHTTP".format(name))
        
        # Add to the LBNodesHTTPS targets
        if elb.register_target(InstanceId, lb_node_https_arn):
            print("Instance {} append to target group LBNodesHTTPS".format(name))
        else:
            print("Instance {} already in target group LBNodesHTTPS".format(name))
