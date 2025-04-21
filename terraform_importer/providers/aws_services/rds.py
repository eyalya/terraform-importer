from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import botocore
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
        self.client = self.get_client("rds")
        self._resources = [
            "aws_db_instance",
            "aws_db_subnet_group"
        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private EC2 resources list.
        Returns:
            list: A copy of the EC2 resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()

    def aws_db_instance(self, resource):
        """
        Validates if the specified RDS DB instance exists and returns its identifier.
        """
        db_identifier = resource['change']['after'].get('identifier')
        if not db_identifier:
            global_logger.error("DB instance identifier is missing.")
            return None
        try:
            response = self.client.describe_db_instances(DBInstanceIdentifier=db_identifier)
            if response.get('DBInstances'):
                return db_identifier
            else:
                global_logger.error(f"DB instance '{db_identifier}' not found.")
        except self.client.exceptions.DBInstanceNotFoundFault:
            global_logger.error(f"DB instance '{db_identifier}' does not exist.")
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"Error retrieving DB instance '{db_identifier}': {e}")
        except Exception as e:
            global_logger.error(f"Unexpected error while retrieving DB instance '{db_identifier}': {e}")
        return None
    
    def aws_db_subnet_group(self, resource):
        """
        Validates if the specified RDS DB subnet group exists and returns its name.
        """
        subnet_group_name = resource['change']['after'].get('name')
        if not subnet_group_name:
            global_logger.error("DB subnet group name is missing.")
            return None
        try:
            response = self.client.describe_db_subnet_groups(DBSubnetGroupName=subnet_group_name)
            if response.get('DBSubnetGroups'):
                return subnet_group_name
            else:
                global_logger.error(f"DB subnet group '{subnet_group_name}' not found.")
        except self.client.exceptions.DBSubnetGroupNotFoundFault:
            global_logger.error(f"DB subnet group '{subnet_group_name}' does not exist.")
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"Error retrieving DB subnet group '{subnet_group_name}': {e}")
        except Exception as e:
            global_logger.error(f"Unexpected error while retrieving DB subnet group '{subnet_group_name}': {e}")
        return None

    #def aws_db_instance(self, resource):
    #    return f"{resource['change']['after']['identifier']}"
#
    #def aws_db_subnet_group(self, resource):
    #     return f"{resource['change']['after']['name']}"