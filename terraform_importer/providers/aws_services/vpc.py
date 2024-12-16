from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import logging
from terraform_importer.providers.aws_services.base import BaseAWSService

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class VPCService(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.client = self.get_client("ec2")
        self._resources = [
            "aws_subnet",
            "aws_route_table",
            "aws_route_table_association"
        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private EC2 resources list.
        Returns:
            list: A copy of the EC2 resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()

    def aws_subnet(self, resource):
        name = resource['change']['after']['tags']['Name']
        response = self.client.describe_subnets(Filters=[{'Name': 'tag:Name', 'Values': [name]}])
        for subnet in response['Subnets']:
            # print (json.dumps(subnet, indent=4, sort_keys=True, default=str)) 
            return subnet['SubnetId']
        return None

    def aws_route_table(self, resource_name, vpc_id):
        response = self.client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}, {'Name': 'tag:Name', 'Values': [resource_name]}])
        for route_table in response['RouteTables']:
            return  id ="{route_table['RouteTableId']}"
        return None

    def aws_route_table_association(self, resource):
        values = resource['change']['after']
        route_table_id = values['route_table_id']
        if "subnet_id" in values and values['subnet_id'] is not None:
            # Handle rule with CIDR block
            rule = f"{values['subnet_id']}/{route_table_id}"
            return rule
        return None