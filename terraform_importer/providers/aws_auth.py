from typing import Optional
import boto3
import logging

class AWSAuthHandler:
    def __init__(self, auth_config: dict):   ## how to refer to the instance attribute??
        self.auth_config = auth_config
        self.logger = logging.getLogger("AWSAuthHandler")
        self.session = self.init_session()
        # TODO: dictionary of providers and their sessions

    def init_session(self) -> boto3.Session:
        """
        Creates a boto3 session based on the authentication configuration.
        Handles different auth scenarios:
        - Profile-based auth
        - Role assumption
        - Default credentials
        """
        ## TODO: Need to fix implementation of this
        try:
            if "profile" in self.auth_config:
                return boto3.Session(profile_name=self.auth_config["profile"])
            
            if "role_arn" in self.auth_config:
                base_session = boto3.Session()
                sts_client = base_session.client('sts')
                assumed_role = sts_client.assume_role(
                    RoleArn=self.auth_config["role_arn"],
                    RoleSessionName="terraform-importer"
                )
                return boto3.Session(
                    aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                    aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                    aws_session_token=assumed_role['Credentials']['SessionToken']
                )
            
            # Default credentials from environment variables or instance profile
            return boto3.Session()
            
        except Exception as e:
            self.logger.error(f"Failed to create AWS session: {str(e)}")
            raise 

    def get_session(self) -> boto3.Session:
        return self.session
