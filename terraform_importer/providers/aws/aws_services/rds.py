from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import botocore
import logging
from terraform_importer.providers.aws.aws_services.base import BaseAWSService

class EC2Service(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.logger = logging.getLogger(__name__)
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
            self.logger.warning("DB instance identifier is missing.")
            return None
        try:
            response = self.client.describe_db_instances(DBInstanceIdentifier=db_identifier)
            if response.get('DBInstances'):
                return db_identifier
            else:
                self.logger.warning(f"DB instance '{db_identifier}' not found.")
        except self.client.exceptions.DBInstanceNotFoundFault:
            self.logger.warning(f"DB instance '{db_identifier}' does not exist.")
        except botocore.exceptions.ClientError as e:
            self.logger.warning(f"Error retrieving DB instance '{db_identifier}': {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error while retrieving DB instance '{db_identifier}': {e}")
        return None
    
    def aws_db_subnet_group(self, resource):
        """
        Validates if the specified RDS DB subnet group exists and returns its name.
        """
        subnet_group_name = resource['change']['after'].get('name')
        if not subnet_group_name:
            self.logger.warning("DB subnet group name is missing.")
            return None
        try:
            response = self.client.describe_db_subnet_groups(DBSubnetGroupName=subnet_group_name)
            if response.get('DBSubnetGroups'):
                return subnet_group_name
            else:
                self.logger.warning(f"DB subnet group '{subnet_group_name}' not found.")
        except self.client.exceptions.DBSubnetGroupNotFoundFault:
            self.logger.warning(f"DB subnet group '{subnet_group_name}' does not exist.")
        except botocore.exceptions.ClientError as e:
            self.logger.warning(f"Error retrieving DB subnet group '{subnet_group_name}': {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error while retrieving DB subnet group '{subnet_group_name}': {e}")
        return None
