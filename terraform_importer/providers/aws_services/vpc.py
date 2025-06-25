from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import botocore
import logging
from terraform_importer.providers.aws_services.base import BaseAWSService

class VPCService(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.logger = logging.getLogger(__name__)
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

    def aws_route_table(self, resource):
        """
        Validates if the AWS Route Table exists by using the 'Name' tag.
    
        Args:
            resource (dict): The Terraform route table resource block.
    
        Returns:
            str: The RouteTableId if found, otherwise None.
        """
        try:
            values = resource.get('change', {}).get('after', {})
            name_tag = values.get('tags', {}).get('Name')
    
            if not name_tag:
                self.logger.error("Missing 'Name' tag in route table resource.")
                return None
    
            response = self.client.describe_route_tables(
                Filters=[
                    {'Name': 'tag:Name', 'Values': [name_tag]}
                ]
            )
    
            for route_table in response.get('RouteTables', []):
                return route_table['RouteTableId']
    
            self.logger.error(f"No route table found with Name tag: {name_tag}")
    
        except Exception as e:
            self.logger.error(f"Error retrieving route table: {e}")
    
        return None
    
    def aws_route_table_association(self, resource):
        """
        Validates the route table association exists and returns the subnet_id/route_table_id key.
        """
        values = resource.get('change', {}).get('after', {})
        route_table_id = values.get('route_table_id')
        subnet_id = values.get('subnet_id')
    
        if not route_table_id or not subnet_id:
            self.logger.error("Route table ID or subnet ID is missing.")
            return None
    
        try:
            response = self.client.describe_route_tables(RouteTableIds=[route_table_id])
            for route_table in response.get('RouteTables', []):
                for assoc in route_table.get('Associations', []):
                    if assoc.get('SubnetId') == subnet_id:
                        return f"{subnet_id}/{route_table_id}"
            self.logger.error(f"No association found for subnet '{subnet_id}' with route table '{route_table_id}'.")
        except Exception as e:
            self.logger.error(f"Error checking route table association: {e}")
        return None
    
    #def aws_subnet(self, resource):
    #    name = resource['change']['after']['tags']['Name']
    #    response = self.client.describe_subnets(Filters=[{'Name': 'tag:Name', 'Values': [name]}])
    #    for subnet in response['Subnets']:
    #        # print (json.dumps(subnet, indent=4, sort_keys=True, default=str)) 
    #        return subnet['SubnetId']
    #    return None
#
    #def aws_route_table(self, resource_name, vpc_id):
    #    response = self.client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}, {'Name': 'tag:Name', 'Values': [resource_name]}])
    #    for route_table in response['RouteTables']:
    #        return route_table['RouteTableId']
    #    return None
#
    #def aws_route_table_association(self, resource):
    #    values = resource['change']['after']
    #    route_table_id = values['route_table_id']
    #    if "subnet_id" in values and values['subnet_id'] is not None:
    #        # Handle rule with CIDR block
    #        rule = f"{values['subnet_id']}/{route_table_id}"
    #        return rule
    #    return None