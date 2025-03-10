from typing import Optional
import boto3
import logging

class AWSAuthHandler:
    def __init__(self, auth_config: dict):   ## how to refer to the instance attribute??
        self.auth_config = auth_config
        self.logger = logging.getLogger("AWSAuthHandler")
        self.profile = None
        self.role_arn = None
        self.region = None
        self.access_key = None
        self.secret_key = None
        self.session = self.init_session()
        # TODO: dictionary of providers and their sessions

    def init_session(self) -> boto3.Session:
        self.set_vars_session()
        
        if self.profile:
            base_session = boto3.Session(profile_name=self.profile, region_name=self.region)
            if self.role_arn:
                return self.assume_role(base_session)
            else:
                return base_session
        
        if self.access_key and self.secret_key:
            base_session = boto3.Session(
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            if self.role_arn:
                return self.assume_role(base_session)
            else:
                return base_session
        
        return self.set_vars_session()
    
    def set_vars_session(self) -> boto3.Session:
        """
        Creates a boto3 session based on the authentication configuration.
        Handles different auth scenarios:
        - Profile-based auth
        - Role assumption
        - Default credentials
        """
        ## TODO: Need to fix implementation of this
        try:
            if "profile" in self.auth_config["expressions"]:
                self.profile = self.auth_config["expressions"]["profile"]
            
            if "assume_role" in self.auth_config["expressions"]:
                self.role_arn = self.auth_config["expressions"]["assume_role"][0]["role_arn"]
            
            if "region" in self.auth_config["expressions"]:
                self.region = self.auth_config["expressions"]["region"]
            
            if "access_key" in self.auth_config["expressions"]:
                self.access_key = self.auth_config["expressions"]["access_key"]
            
            if "secret_key" in self.auth_config["expressions"]:
                self.secret_key = self.auth_config["expressions"]["secret_key"]
            
        except Exception as e:
            self.logger.error(f"Failed to create AWS session: {str(e)}")
            raise 

    def get_session(self) -> boto3.Session:
        return self.session

    def assume_role(self, session: boto3.Session) -> boto3.Session:
        sts_client = session.client('sts')
        assumed_role = sts_client.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName="terraform-importer"
        )
        session = boto3.Session(
            aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
            aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
            aws_session_token=assumed_role['Credentials']['SessionToken']
        )

        return session
