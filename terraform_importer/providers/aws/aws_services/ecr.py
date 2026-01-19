from typing import List, Optional, Dict
import boto3
import botocore.exceptions
import logging
from terraform_importer.providers.aws.aws_services.base import BaseAWSService

class ECRService(BaseAWSService):
    """
    Handles ECR (Elastic Container Registry) related resources (e.g., repositories, registry scanning configuration).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.logger = logging.getLogger(__name__)
        self.client = self.get_client("ecr")
        self._resources = [
            "aws_ecr_repository",
            "aws_ecr_lifecycle_policy",
            "aws_ecr_registry_scanning_configuration"
        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private ECR resources list.
        Returns:
            list: A copy of the ECR resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()

    def aws_ecr_repository(self, resource):
        """
        Retrieves the AWS ECR repository name after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The ECR repository name if it exists, otherwise None.
        """
        repository_name = None
        try:
            repository_name = resource['change']['after'].get('name')
            
            if not repository_name:
                self.logger.warning("ECR repository name is missing in the resource data.")
                return None
            
            # Check if the repository exists
            try:
                response = self.client.describe_repositories(repositoryNames=[repository_name])
                
                # If the repository exists, return its name
                if response.get('repositories'):
                    return repository_name
                
                self.logger.warning(f"ECR repository '{repository_name}' not found.")
                return None
                
            except self.client.exceptions.RepositoryNotFoundException:
                self.logger.warning(f"ECR repository '{repository_name}' does not exist.")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'RepositoryNotFoundException':
                repo_name = repository_name if repository_name else 'unknown'
                self.logger.warning(f"ECR repository '{repo_name}' does not exist.")
            else:
                self.logger.warning(f"AWS ClientError while validating ECR repository: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_ecr_lifecycle_policy(self, resource):
        """
        Retrieves the AWS ECR lifecycle policy identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The repository name (identifier for the lifecycle policy) if it exists, otherwise None.
        """
        repository_name = None
        try:
            repository_name = resource['change']['after'].get('repository')
            
            if not repository_name:
                self.logger.warning("ECR lifecycle policy repository name is missing in the resource data.")
                return None
            
            # Check if the lifecycle policy exists for the repository
            try:
                response = self.client.get_lifecycle_policy(repositoryName=repository_name)
                
                # If the lifecycle policy exists, return the repository name as identifier
                if response:
                    return repository_name
                
                self.logger.warning(f"ECR lifecycle policy for repository '{repository_name}' not found.")
                return None
                
            except self.client.exceptions.LifecyclePolicyNotFoundException:
                self.logger.warning(f"ECR lifecycle policy for repository '{repository_name}' does not exist.")
                return None
            except self.client.exceptions.RepositoryNotFoundException:
                self.logger.warning(f"ECR repository '{repository_name}' does not exist.")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'LifecyclePolicyNotFoundException':
                repo_name = repository_name if repository_name else 'unknown'
                self.logger.warning(f"ECR lifecycle policy for repository '{repo_name}' does not exist.")
            elif error_code == 'RepositoryNotFoundException':
                repo_name = repository_name if repository_name else 'unknown'
                self.logger.warning(f"ECR repository '{repo_name}' does not exist.")
            else:
                self.logger.warning(f"AWS ClientError while validating ECR lifecycle policy: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_ecr_registry_scanning_configuration(self, resource):
        """
        Retrieves the AWS ECR registry scanning configuration after validating its existence.
        
        Note: ECR registry scanning configuration is a single account-level resource.
        There can only be one registry scanning configuration per AWS account.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: A fixed identifier for the registry scanning configuration if it exists, otherwise None.
        """
        try:
            # Validate resource structure first
            if 'change' not in resource or 'after' not in resource.get('change', {}):
                self.logger.warning("Missing expected key in resource: 'change' or 'change.after'")
                return None
            
            # ECR registry scanning configuration is account-level, so we check if it exists
            try:
                response = self.client.get_registry_scanning_configuration()
                
                # If we can get the registry scanning configuration, it exists
                # Return a fixed identifier since there's only one per account
                if response:
                    return "default"
                
                return None
                
            except botocore.exceptions.ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if error_code in ['AccessDeniedException', 'InvalidParameterException', 'ValidationException']:
                    self.logger.warning(f"Unable to access ECR registry scanning configuration: {e}")
                else:
                    self.logger.warning(f"AWS ClientError while validating ECR registry scanning configuration: {e}")
                return None
                
        except KeyError as e:
            self.logger.warning(f"Missing expected key in resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None
