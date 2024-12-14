from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import logging
from terraform_importer.providers.aws_services.base import BaseAWSService

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class EC2Service(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.client = self.get_client("ec2")
        self._resources = [
            "aws_security_group",
            "aws_security_group_rule"
        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private EC2 resources list.
        Returns:
            list: A copy of the EC2 resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()
    
        
    # Function to generate an import block for Elastic IP (EIP)
    def aws_security_group(self, resource):
        name = resource['change']['after']['name']
        response = self.client.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [name]}])

        if len(response['SecurityGroups']) > 0:
            return response['SecurityGroups'][0]['GroupId']
        return None 
    
    def aws_security_group_rule(self, resource):
        values = resource['change']['after']
        main_string = f"{values['security_group_id']}_{values['type']}_{values['protocol']}_{values['from_port']}_{values['to_port']}"
        if "cidr_blocks" in values and values['cidr_blocks'] is not None:
            # Handle rule with CIDR block
            return f"{main_string}_{'_'.join(values['cidr_blocks'])}"
        elif "source_security_group_id" in values and values['source_security_group_id'] is not None:
            # Handle rule with CIDR block
            return f"{main_string}_{values['source_security_group_id']}"
        
        return None
