from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import botocore
import logging
from terraform_importer.providers.aws_services.base import BaseAWSService

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class IAMService(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.client = self.get_client("iam")
        self._resources = [
            "aws_iam_role",
            "aws_iam_policy",
            "aws_iam_role_policy",
            "aws_iam_role_policy_attachment",
            "aws_iam_user",
            "aws_iam_group",
            "aws_iam_instance_profile"

        ]
    
    def get_resource_list(self) -> List[str]:
        """
        Getter for the private EC2 resources list.
        Returns:
            list: A copy of the EC2 resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()

    def aws_iam_role(self, resource):
        role_name = resource['change']['after'].get('name')
        if not role_name:
            global_logger.error("Missing role name.")
            return None
        try:
            self.client.get_role(RoleName=role_name)
            return role_name
        except self.client.exceptions.NoSuchEntityException:
            global_logger.error(f"IAM role '{role_name}' does not exist.")
        return None

    def aws_iam_policy(self, resource):
        policy_name = resource['change']['after'].get('name')
        if not policy_name:
            global_logger.error("Missing policy name.")
            return None
        policy_arn = f"arn:aws:iam::{self.session.client('sts').get_caller_identity()['Account']}:policy/{policy_name}"
        try:
            self.client.get_policy(PolicyArn=policy_arn)
            return policy_arn
        except self.client.exceptions.NoSuchEntityException:
            global_logger.error(f"IAM policy '{policy_arn}' does not exist.")
        return None

    def aws_iam_role_policy(self, resource):
        role_name = resource['change']['after'].get('role')
        policy_name = resource['change']['after'].get('name')
        if not role_name or not policy_name:
            global_logger.error("Missing role or policy name.")
            return None
        try:
            self.client.get_role_policy(RoleName=role_name, PolicyName=policy_name)
            return f"{role_name}:{policy_name}"
        except self.client.exceptions.NoSuchEntityException:
            global_logger.error(f"IAM role policy '{policy_name}' for role '{role_name}' does not exist.")
        return None

    def aws_iam_role_policy_attachment(self, resource):
        role = resource['change']['after'].get('role')
        policy_arn = resource['change']['after'].get('policy_arn')
        if not role or not policy_arn:
            global_logger.error("Missing role or policy ARN.")
            return None
        try:
            attached_policies = self.client.list_attached_role_policies(RoleName=role).get("AttachedPolicies", [])
            if any(p["PolicyArn"] == policy_arn for p in attached_policies):
                return f"{role}/{policy_arn}"
            global_logger.error(f"Policy '{policy_arn}' not attached to role '{role}'.")
        except self.client.exceptions.NoSuchEntityException:
            global_logger.error(f"IAM role '{role}' does not exist.")
        return None

    def aws_iam_user(self, resource):
        user_name = resource['change']['after'].get('name')
        if not user_name:
            global_logger.error("Missing user name.")
            return None
        try:
            self.client.get_user(UserName=user_name)
            return user_name
        except self.client.exceptions.NoSuchEntityException:
            global_logger.error(f"IAM user '{user_name}' does not exist.")
        return None

    def aws_iam_group(self, resource):
        group_name = resource['change']['after'].get('name')
        if not group_name:
            global_logger.error("Missing group name.")
            return None
        try:
            self.client.get_group(GroupName=group_name)
            return group_name
        except self.client.exceptions.NoSuchEntityException:
            global_logger.error(f"IAM group '{group_name}' does not exist.")
        return None

    def aws_iam_instance_profile(self, resource):
        profile_name = resource['change']['after'].get('name')
        if not profile_name:
            global_logger.error("Missing instance profile name.")
            return None
        try:
            self.client.get_instance_profile(InstanceProfileName=profile_name)
            return profile_name
        except self.client.exceptions.NoSuchEntityException:
            global_logger.error(f"IAM instance profile '{profile_name}' does not exist.")
        return None
#
    #def aws_iam_role(self, resource):
    #    return resource['change']['after']['name']
#
    #def aws_iam_policy(self, resource):
    #    return f"arn:aws:iam::891513744586:policy/{resource['change']['after']['name']}"
    #
    #def aws_iam_role_policy(self, resource):
    #    role_name = resource['change']['after']['role']
    #    name = resource['change']['after']['name']
    #    return f"{role_name}:{name}"
    #
    #def aws_iam_role_policy_attachment(self, resource):
    #    return f"{resource['change']['after']['role']}/{resource['change']['after']['policy_arn']}"
    #
    #def aws_iam_user(self, resource):
    #    return resource['change']['after']['name']
#
    #def aws_iam_group(self, resource):
    #    return f"{resource['change']['after']['name']}"
#
    #def aws_iam_instance_profile(self, resource):
    #    return resource['change']['after']['name']