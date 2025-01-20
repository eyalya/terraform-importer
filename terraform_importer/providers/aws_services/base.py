from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import logging

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")


# Abstract Base Class for AWS Services
class BaseAWSService(ABC):
    """
    Abstract base class for AWS service handlers (e.g., EC2, VPC).
    """

    def __init__(self, sessions: boto3.Session ):
        # Shared data for all AWS services
        self.sessions = sessions
    
    def get_client(self, service_name: str, provider: str):
        """
        Creates a boto3 client for the specified AWS service.
        Args:
            service_name (str): The name of the AWS service (e.g., 'ec2', 'vpc').
            provider (str): The name of the provider (e.g., 'aws').
        Returns:
            boto3.client: A boto3 client for the specified service.
        """
        return self.sessions[provider].client(service_name)


    @abstractmethod
    def get_resource_list(self) -> List[str]:
        """
        """
        pass
    
    def get_id(self, resource_type: str, resource_block: Dict, sessions: Dict) -> Optional[str]:
        """
        Fetches the ID for a specific resource type and resource block.
        Args:
            resource_type (str): The type of the resource (e.g., 'aws_instance').
            resource_block (Dict): The resource configuration block.
        Returns:
            Optional[str]: Resource ID if found, or None if not found.
        """
        if hasattr(self, resource_type):
            method = getattr(self, resource_type)
            return method(resource_block, sessions)
        else:
            global_logger.info(f"No such resource_type: {resource_type}")
            return None

    
