from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import botocore.exceptions
import logging
from terraform_importer.providers.aws.aws_services.base import BaseAWSService

class ECSService(BaseAWSService):
    """
    Handles EC2-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.logger = logging.getLogger(__name__)
        self.client = self.get_client("ecs")
        self.sd_client = self.get_client("servicediscovery")
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
        """
        Retrieves the AWS ECS Service name after validating its existence.
    
        Args:
            resource (dict): The resource block from Terraform.
    
        Returns:
            str: The AWS ECS Service name if it exists, otherwise None.
        """
        try:
            # Extract cluster name and service name dynamically
            cluster_name = resource['change']['after'].get('cluster')
            service_name = resource['change']['after'].get('name')
    
            if not cluster_name or not service_name:
                self.logger.error(f"Missing 'cluster' or 'name' in resource data: {resource['change']['after']}")
                return None
    
            # **Validation Step**: Check if the ECS Service exists in AWS
            try:
                response = self.client.describe_services(
                    cluster=cluster_name,
                    services=[service_name]
                )
    
                if response.get('services') and response['services'][0].get('status') != "INACTIVE":
                    return f"{cluster_name}/{service_name}"
    
                self.logger.error(f"ECS Service '{service_name}' not found in cluster '{cluster_name}' or is INACTIVE")
                return None
    
            except botocore.exceptions.ClientError as e:
                self.logger.error(f"AWS ClientError while validating ECS Service: {e}")
                return None
    
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.BotoCoreError as e:
            self.logger.error(f"AWS BotoCoreError: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
    
        return None


    def aws_ecs_task_definition(self, resource):
        """
        Validates and retrieves the ECS Task Definition ARN.
    
        Args:
            resource (dict): The Terraform resource block.
    
        Returns:
            str: The ECS Task Definition ARN if it exists, otherwise None.
        """
        try:
            # Extract the task family name from Terraform resource data
            name = resource['change']['after'].get('family')
            
            if not name:
                self.logger.error("Missing 'family' key in resource data.")
                return None
    
            # **Validation Step**: Check if the ECS Task Definition exists
            try:
                response = self.client.describe_task_definition(taskDefinition=name)
                return response['taskDefinition']['taskDefinitionArn']
    
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'ClientException' or "not found" in str(e):
                    self.logger.error(f"ECS Task Definition '{name}' does not exist.")
                else:
                    self.logger.error(f"AWS ClientError while checking ECS Task Definition: {e}")
                return None
    
        except botocore.exceptions.BotoCoreError as e:
            self.logger.error(f"AWS BotoCoreError: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
    
        return None


    def aws_ecs_cluster_capacity_providers(self, resource):
        """
        Validates if the ECS cluster exists and returns its name.
    
        Args:
            resource (dict): The Terraform resource block.
    
        Returns:
            str: The ECS Cluster name if it exists, otherwise None.
        """
        cluster_name = resource['change']['after'].get('cluster_name')
    
        if not cluster_name:
            self.logger.error("Cluster name is missing in the resource data.")
            return None
    
        try:
            # Validate if the ECS Cluster exists
            response = self.client.describe_clusters(clusters=[cluster_name])
    
            # Check if the cluster exists in the response
            if response['clusters']:
                return cluster_name
            else:
                self.logger.error(f"ECS Cluster '{cluster_name}' does not exist.")
                return None
    
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating ECS Cluster: {e}")
        except botocore.exceptions.BotoCoreError as e:
            self.logger.error(f"AWS BotoCoreError: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
    
        return None

    def aws_service_discovery_service(self, resource):
        """
        Validates if the AWS Service Discovery service exists and returns its ID.
    
        Args:
            resource (dict): The Terraform resource block.
    
        Returns:
            str: The Service Discovery service ID if it exists, otherwise None.
        """
        try:
            # Extract required values
            namespace_id = resource['change']['after'].get('dns_config', [{}])[0].get('namespace_id')
            service_name = resource['change']['after'].get('name')
    
            if not namespace_id or not service_name:
                self.logger.error("Missing required values: namespace_id or service_name.")
                return None
    
            # Use paginator to iterate through services in the given namespace
            paginator = self.sd_client.get_paginator('list_services')
    
            for page in paginator.paginate(Filters=[
                {'Name': 'NAMESPACE_ID', 'Values': [namespace_id], 'Condition': 'EQ'}
            ]):
                for service in page.get('Services', []):
                    if service.get('Name') == service_name:
                        return service.get('Id')
    
            # If no match is found
            self.logger.error(f"Service Discovery service '{service_name}' not found in namespace '{namespace_id}'.")
            return None
    
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating Service Discovery service: {e}")
        except botocore.exceptions.BotoCoreError as e:
            self.logger.error(f"AWS BotoCoreError: {e}")
        except KeyError as e:
            self.logger.error(f"Missing key in resource data: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
    
        return None