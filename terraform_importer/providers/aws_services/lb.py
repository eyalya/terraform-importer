from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import logging
from terraform_importer.providers.aws_services.base import BaseAWSService

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class LoadBalancerService(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.client = self.get_client("'elbv2'")
        self._resources = [
            "aws_lb_target_group",
            "aws_lb_listener"
        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private EC2 resources list.
        Returns:
            list: A copy of the EC2 resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()

def aws_lb_target_group(self, resource):
    name = resource['change']['after']['name']
    try:
        # List all target groups
        paginator = self.client.get_paginator('describe_target_groups')
        for page in paginator.paginate():
            for target_group in page['TargetGroups']:
                if target_group['TargetGroupName'] == name:
                    return target_group['TargetGroupArn']
    except self.client.exceptions.ClientError as e:
        global_logger.error(f"Error retrieving target group: {e}")
    return None  # Return None if no target group is found with the given name

def aws_lb_listener(self, resource):

    target_group_arn = resource['change']['after']['default_action']['target_group_arn']
    port = resource['change']['after']['port']
    protocol = resource['change']['after']['protocol']

    load_balancers = self.client.describe_load_balancers()
    
    # Step 2: Iterate through each load balancer
    for lb in load_balancers['LoadBalancers']:
        lb_arn = lb['LoadBalancerArn']

        # Step 3: Get listeners for each load balancer
        listeners = self.client.describe_listeners(LoadBalancerArn=lb_arn)

        # Step 4: Check each listener for port, protocol, and target group ARN
        for listener in listeners['Listeners']:
            if listener['Port'] == port and listener['Protocol'] == protocol:
                for action in listener['DefaultActions']:
                    if action.get('TargetGroupArn') == target_group_arn:
                        return listener['ListenerArn']
        else:
            global_logger.error("No matching listener found")

    return None  # Return None if no matching listener found

#def aws_lb_listener_rule(self,resource):
