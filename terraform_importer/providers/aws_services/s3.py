from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import botocore
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
        self.client = self.get_client("s3")
        self._resources = [
            "aws_s3_bucket",
            "aws_s3_bucket_notification",
            "aws_s3_bucket_ownership_controls",
            "aws_s3_bucket_policy",
            "aws_s3_bucket_public_access_block",
            "aws_s3_bucket_server_side_encryption_configuration",
            "aws_s3_bucket_lifecycle_configuration",
            "aws_s3_bucket_versioning",
            "aws_s3_bucket_acl"

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
        bucket = resource['change']['after'].get('bucket')
        if not bucket:
            global_logger.error("Bucket name is missing.")
            return None
        try:
            self.client.head_bucket(Bucket=bucket)
            return bucket
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"S3 bucket '{bucket}' not found or inaccessible: {e}")
        return None
    
    def aws_s3_bucket_notification(self, resource):
        bucket = resource['change']['after'].get('bucket')
        try:
            self.client.head_bucket(Bucket=bucket)
            config = self.client.get_bucket_notification_configuration(Bucket=bucket)
            if any(config.get(k) for k in ['TopicConfigurations', 'QueueConfigurations', 'LambdaFunctionConfigurations']):
                return bucket
            global_logger.error(f"No notification config found for bucket '{bucket}'.")
        except Exception as e:
            global_logger.error(f"Error checking notification config for bucket '{bucket}': {e}")
        return None
    
    def aws_s3_bucket_ownership_controls(self, resource):
        bucket = resource['change']['after'].get('bucket')
        try:
            self.client.head_bucket(Bucket=bucket)
            self.client.get_bucket_ownership_controls(Bucket=bucket)
            return bucket
        except Exception as e:
            global_logger.error(f"Error checking ownership controls for bucket '{bucket}': {e}")
        return None
    
    def aws_s3_bucket_policy(self, resource):
        bucket = resource['change']['after'].get('bucket')
        try:
            self.client.head_bucket(Bucket=bucket)
            self.client.get_bucket_policy(Bucket=bucket)
            return bucket
        except Exception as e:
            global_logger.error(f"Error checking policy for bucket '{bucket}': {e}")
        return None
    
    def aws_s3_bucket_public_access_block(self, resource):
        bucket = resource['change']['after'].get('bucket')
        try:
            self.client.head_bucket(Bucket=bucket)
            self.client.get_public_access_block(Bucket=bucket)
            return bucket
        except Exception as e:
            global_logger.error(f"Error checking public access block for bucket '{bucket}': {e}")
        return None
    
    def aws_s3_bucket_server_side_encryption_configuration(self, resource):
        bucket = resource['change']['after'].get('bucket')
        try:
            self.client.head_bucket(Bucket=bucket)
            self.client.get_bucket_encryption(Bucket=bucket)
            return bucket
        except Exception as e:
            global_logger.error(f"Error checking encryption config for bucket '{bucket}': {e}")
        return None
    
    def aws_s3_bucket_lifecycle_configuration(self, resource):
        bucket = resource['change']['after'].get('bucket')
        try:
            self.client.head_bucket(Bucket=bucket)
            config = self.client.get_bucket_lifecycle_configuration(Bucket=bucket)
            if config.get("Rules"):
                return bucket
            global_logger.error(f"No lifecycle rules found for bucket '{bucket}'.")
        except Exception as e:
            global_logger.error(f"Error checking lifecycle config for bucket '{bucket}': {e}")
        return None
    
    def aws_s3_bucket_versioning(self, resource):
        bucket = resource['change']['after'].get('bucket')
        try:
            self.client.head_bucket(Bucket=bucket)
            versioning = self.client.get_bucket_versioning(Bucket=bucket)
            if versioning.get("Status") in ("Enabled", "Suspended"):
                return bucket
            global_logger.error(f"Versioning is not enabled or suspended for bucket '{bucket}'.")
        except Exception as e:
            global_logger.error(f"Error checking versioning for bucket '{bucket}': {e}")
        return None
    
    def aws_s3_bucket_acl(self, resource):       
        bucket = resource['change']['after'].get('bucket')
        acl  = resource['change']['after'].get('acl')
        expected_owner = resource['change']['after'].get('expected_bucket_owner')
    
        if not bucket:
            global_logger.error("Bucket name is missing.")
            return None
    
        try:
            self.client.head_bucket(Bucket=bucket)
            self.client.get_bucket_acl(Bucket=bucket)
    
            parts = [bucket]
            if expected_owner:
                parts.append(expected_owner)
            if acl:
                parts.append(acl)
    
            return ",".join(parts)
        except Exception as e:
            global_logger.error(f"Error checking ACL for bucket '{bucket}': {e}")
        return None
    
    #def aws_s3_bucket(self, resource):
    #    return resource['change']['after']['bucket']
#
    #def aws_s3_bucket_notification(self,resource):
    #    return resource['change']['after']['bucket']
#
    #def aws_s3_bucket_ownership_controls(self,resource):
    #    return resource['change']['after']['bucket']
#
    #def aws_s3_bucket_policy(self, resource):
    #    return resource['change']['after']['bucket']
#
    #def aws_s3_bucket_public_access_block(self, resource):
    #    return resource['change']['after']['bucket']
#
    #def aws_s3_bucket_server_side_encryption_configuration(self, resource):
    #    return resource['change']['after']['bucket']
#
    #def aws_s3_bucket_lifecycle_configuration(self, resource):
    #    return resource['change']['after']['bucket']
#
    #def aws_s3_bucket_versioning(self, resource):
    #    return resource['change']['after']['bucket']
#
    #def aws_s3_bucket_acl(self,resource):       
    #    acl  = resource['change']['after']['acl']
    #    name = resource['change']['after']['bucket']
    #    expected_bucket_owner = resource['change']['after']['expected_bucket_owner']
#
    #    if acl and expected_bucket_owner: 
    #        return f"{name},{expected_bucket_owner},{acl}"
    #    elif acl and expected_bucket_owner is None:
    #        return f"{name},{acl}"
    #    elif not acl and expected_bucket_owner is None:
    #        return name
    #    elif not acl and expected_bucket_owner:
    #        return f"{name},{expected_bucket_owner}"
    #    return None
#