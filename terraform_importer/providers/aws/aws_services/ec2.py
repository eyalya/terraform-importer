from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import botocore.exceptions
import logging
from terraform_importer.providers.aws.aws_services.base import BaseAWSService

class EC2Service(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.logger = logging.getLogger(__name__)
        self.client = self.get_client("ec2")
        self._resources = [
            "aws_security_group",
            "aws_security_group_rule",
            "aws_autoscaling_group",
            "aws_key_pair"
        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private EC2 resources list.
        Returns:
            list: A copy of the EC2 resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()
    
    def aws_security_group(self, resource):
        """
        Retrieves the AWS Security Group ID after validating its existence.
    
        Args:
            resource (dict): The resource block from Terraform.
    
        Returns:
            str: The AWS Security Group ID if it exists, otherwise None.
        """
        try:
            name = resource['change']['after']['name']
    
            response = self.client.describe_security_groups(
                Filters=[{'Name': 'group-name', 'Values': [name]}]
            )
    
            if response.get('SecurityGroups'):  # Check if SecurityGroups key exists and is not empty
                return response['SecurityGroups'][0]['GroupId']
    
            self.logger.error(f"Security Group '{name}' not found")
            return None
    
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.BotoCoreError as e:
            self.logger.error(f"AWS SDK error while describing security groups: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
    
        return None
    

    def aws_security_group_rule(self, resource):
        """
        Retrieves the AWS Security Group Rule ID after validating its existence.
    
        Args:
            resource (dict): The resource block from Terraform.
    
        Returns:
            str: The AWS Security Group Rule ID if it exists, otherwise None.
        """
        try:
            values = resource['change']['after']
    
            security_group_id = values.get('security_group_id')
            if not security_group_id:
                self.logger.error("Missing security_group_id in resource data")
                return None
    
            # Construct the main rule identifier string
            main_string = f"{security_group_id}_{values['type']}_{values['protocol']}_{values['from_port']}_{values['to_port']}"
    
            # Determine the source (CIDR block or Security Group ID)
            if "cidr_blocks" in values and values['cidr_blocks']:
                rule_identifier = f"{main_string}_{'_'.join(values['cidr_blocks'])}"
            elif "source_security_group_id" in values and values['source_security_group_id']:
                rule_identifier = f"{main_string}_{values['source_security_group_id']}"
            else:
                self.logger.error("No valid source (CIDR block or source_security_group_id) found")
                return None
    
            # **Validation Step**: Check if the rule exists in AWS
            try:
                response = self.client.describe_security_group_rules(
                    Filters=[{'Name': 'group-id', 'Values': [security_group_id]}]
                )
                existing_rules = response.get('SecurityGroupRules', [])
    
                for rule in existing_rules:
                    if rule_identifier in str(rule):  # Convert rule to string for easier matching
                        return rule_identifier
    
                self.logger.error(f"Security Group Rule '{rule_identifier}' not found in AWS")
                return None
    
            except botocore.exceptions.ClientError as e:
                self.logger.error(f"AWS ClientError while validating rule: {e}")
                return None
    
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.BotoCoreError as e:
            self.logger.error(f"AWS BotoCoreError: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
    
        return None


    def aws_autoscaling_group(self, resource):
        """
        Retrieves the AWS Auto Scaling Group (ASG) name after validating its existence.
    
        Args:
            resource (dict): The resource block from Terraform.
    
        Returns:
            str: The AWS Auto Scaling Group name if it exists, otherwise None.
        """
        try:
            asg_name = resource['change']['after'].get('name')
    
            if not asg_name:
                self.logger.error("Missing 'name' in resource data")
                return None
    
            # **Validation Step**: Check if the Auto Scaling Group exists in AWS
            try:
                response = self.client.describe_auto_scaling_groups(
                    AutoScalingGroupNames=[asg_name]
                )
                if response.get('AutoScalingGroups'):
                    return asg_name
    
                self.logger.error(f"Auto Scaling Group '{asg_name}' not found in AWS")
                return None
    
            except botocore.exceptions.ClientError as e:
                self.logger.error(f"AWS ClientError while validating ASG: {e}")
                return None
    
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.BotoCoreError as e:
            self.logger.error(f"AWS BotoCoreError: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
    
        return None

    #def aws_key_pair(self, resource):
    #    return resource['change']['after']['key_name']

    def aws_key_pair(self, resource):
        """
        Retrieves the AWS Key Pair name after validating its existence.
    
        Args:
            resource (dict): The resource block from Terraform.
    
        Returns:
            str: The AWS Key Pair name if it exists, otherwise None.
        """
        try:
            key_name = resource['change']['after'].get('key_name')
    
            if not key_name:
                self.logger.error("Missing 'key_name' in resource data")
                return None
    
            # **Validation Step**: Check if the Key Pair exists in AWS
            try:
                response = self.client.describe_key_pairs(KeyNames=[key_name])
                if response.get('KeyPairs'):
                    return key_name
    
                self.logger.error(f"Key Pair '{key_name}' not found in AWS")
                return None
    
            except botocore.exceptions.ClientError as e:
                self.logger.error(f"AWS ClientError while validating Key Pair: {e}")
                return None
    
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.BotoCoreError as e:
            self.logger.error(f"AWS BotoCoreError: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
    
        return None
