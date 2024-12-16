from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import logging
from terraform_importer.providers.aws_services.base import BaseAWSService

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class ECSService(BaseAWSService):
    """
    Handles EC2-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.client = self.get_client("ecs")
        self._resources = [
            "aws_ecs_service",
            "aws_ecs_task_definition",
            "aws_ecs_cluster_capacity_providers",
            "aws_service_discovery_service"
        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private EC2 resources list.
        Returns:
            list: A copy of the EC2 resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()
    
        
    def aws_ecs_service(self, resource):
        name = resource['change']['after']['name']
        return f"development/{name}"

    def aws_ecs_task_definition(self, resource):
        name = resource['change']['after']['family']
        try:
            # Describe the task definition
            response = self.client.describe_task_definition(taskDefinition=name)
            # Extract and return the Task Definition ARN
            return  response['taskDefinition']['taskDefinitionArn']
        except self.client.exceptions.ClientException as e:
            global_logger.error(f"Error retrieving task definition: {e}")
            return None

    def aws_ecs_cluster_capacity_providers(self, resource):
        return f"{resource['change']['after']['cluster_name']}"

    def aws_service_discovery_service(self, resource_name, vpc_id):
        response = service_discovery_client.list_namespaces(Filters={'Name': 'VPC', 'Values': [vpc_id]})
        for namespace in response['Namespaces']:
            if namespace['Name'] == resource_name:
                return {namespace['Id']}
        return None