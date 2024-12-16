from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import logging
from terraform_importer.providers.aws_services.base import BaseAWSService

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class IAMService(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        #self.client = self.get_client("ec2")
        self._resources = [
            "aws_iam_role",
            "aws_iam_policy",
            "aws_iam_role_policy",
            "aws_iam_role_policy_attachment",
            "aws_iam_user",
            "aws_iam_group",
            "aws_iam_instance_profile"

        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private EC2 resources list.
        Returns:
            list: A copy of the EC2 resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()

    def aws_iam_role(self, resource):
        return resource['change']['after']['name']

    def aws_iam_policy(self, resource):
        return f"arn:aws:iam::891513744586:policy/{resource['change']['after']['name']}"
    
    def aws_iam_role_policy(self, resource):
        role_name = resource['change']['after']['role']
        name = resource['change']['after']['name']
        return f"{role_name}:{name}"
    
    def aws_iam_role_policy_attachment(self, resource):
        return f"{resource['change']['after']['role']}/{resource['change']['after']['policy_arn']}"
    
    def aws_iam_user(self, resource):
        return resource['change']['after']['name']

    def aws_iam_group(self, resource):
        return f"{resource['change']['after']['name']}"

    def aws_iam_instance_profile(self, resource):
        return resource['change']['after']['name']