from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import botocore
import logging
from terraform_importer.providers.aws.aws_services.base import BaseAWSService

class LoadBalancerService(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.logger = logging.getLogger(__name__)
        self.client = self.get_client("elbv2")
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
        """
        Validates if the specified Load Balancer Target Group exists and returns its ARN.
        """
        name = resource['change']['after'].get('name')
        if not name:
            self.logger.error("Target group name is missing.")
            return None
        try:
            paginator = self.client.get_paginator('describe_target_groups')
            for page in paginator.paginate():
                for target_group in page.get('TargetGroups', []):
                    if target_group.get('TargetGroupName') == name:
                        return target_group.get('TargetGroupArn')
            self.logger.error(f"Target group '{name}' not found.")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"Error retrieving target group '{name}': {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error while retrieving target group '{name}': {e}")
        return None

    def aws_lb_listener(self, resource):
        """
        Validates if the specified Load Balancer Listener exists and returns its ARN.
        """
        try:
            lb_arn = resource['change']['after'].get('load_balancer_arn')
            port = resource['change']['after'].get('port')
            protocol = resource['change']['after'].get('protocol')
    
            if not lb_arn or port is None or not protocol:
                self.logger.error("Missing required values: load_balancer_arn, port, or protocol.")
                return None
    
            response = self.client.describe_listeners(LoadBalancerArn=lb_arn)
            for listener in response.get('Listeners', []):
                if listener.get('Port') == port and listener.get('Protocol') == protocol:
                    return listener.get('ListenerArn')
    
            self.logger.error(f"No matching listener found on Load Balancer '{lb_arn}' for port {port} and protocol '{protocol}'.")
    
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"ClientError while retrieving listener for Load Balancer '{lb_arn}': {e}")
        except KeyError as e:
            self.logger.error(f"Missing key in resource data: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error while retrieving listener: {e}")
    
        return None

    
