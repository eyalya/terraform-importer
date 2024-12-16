from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import logging
from terraform_importer.providers.aws_services.base import BaseAWSService

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class S3Service(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        #self.client = self.get_client("s3")
        self._resources = [
            "aws_s3_bucket",
            "aws_s3_bucket_notification",
            "aws_s3_bucket_ownership_controls",
            "aws_s3_bucket_policy",
            "aws_s3_bucket_public_access_block",
            "aws_s3_bucket_server_side_encryption_configuration",
            "aws_s3_bucket_lifecycle_configuration",
            "aws_s3_bucket_versioning"

        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private EC2 resources list.
        Returns:
            list: A copy of the EC2 resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()

    def aws_s3_bucket(self, resource):
        return resource['change']['after']['bucket']

    def aws_s3_bucket_notification(self,resource):
        return resource['change']['after']['bucket']

    def aws_s3_bucket_ownership_controls(self,resource):
        return resource['change']['after']['bucket']

    def aws_s3_bucket_policy(self, resource):
        return resource['change']['after']['bucket']

    def aws_s3_bucket_public_access_block(self, resource):
        return resource['change']['after']['bucket']

    def aws_s3_bucket_server_side_encryption_configuration(self, resource):
        return resource['change']['after']['bucket']

    def aws_s3_bucket_lifecycle_configuration(self, resource):
        return resource['change']['after']['bucket']

    def aws_s3_bucket_versioning(self, resource):
        return resource['change']['after']['bucket']

    #def aws_s3_bucket_acl(self,resource):       #TODO: check docomantation 
    #    return resource['change']['after']['bucket']
