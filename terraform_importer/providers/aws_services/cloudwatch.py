from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import botocore.exceptions
import logging
from terraform_importer.providers.aws_services.base import BaseAWSService

class CloudWatchService(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.logger = logging.getLogger(__name__)
        self.logs_client = self.get_client("logs")
        self.events_client = self.get_client("events")
        # Get account ID using STS client
        sts_client = self.get_client('sts')
        self.account_id = sts_client.get_caller_identity()['Account']
        # Get region from session
        self.region = session.region_name
        self._resources = [
            "aws_cloudwatch_query_definition",
            "aws_cloudwatch_event_target",
            "aws_cloudwatch_log_group",
            "aws_cloudwatch_metric_alarm",
            "aws_cloudwatch_event_rule",
            "aws_cloudwatch_log_metric_filter",
            "aws_cloudwatch_query_definition"
        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private EC2 resources list.
        Returns:
            list: A copy of the EC2 resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()

    #def aws_cloudwatch_event_target(self, resource):
    #    return f"{resource['change']['after']['rule']}/{resource['change']['after']['target_id']}"
    
    def aws_cloudwatch_event_target(self, resource):
        """
        Retrieves the AWS CloudWatch Event Target ID after validating its existence.
    
        Args:
            resource (dict): The resource block from Terraform.
    
        Returns:
            str: The AWS CloudWatch Event Target ID if it exists, otherwise None.
        """
        rule_name = resource['change']['after']['rule']
        target_id = resource['change']['after']['target_id']
    
        try:
            response = self.events_client.list_targets_by_rule(Rule=rule_name)
            targets = response.get("Targets", [])
    
            # Check if the target_id exists in the rule
            for target in targets:
                if target.get("Id") == target_id:
                    return f"{rule_name}/{target_id}"
    
            # If target not found
            self.logger.error(f"CloudWatch Event Target '{target_id}' not found in rule '{rule_name}'")
            return None
    
        except Exception as e:
            self.logger.error(f"Failed to validate CloudWatch Event Target: {e}")
            return None


    def aws_cloudwatch_log_group(self, resource):
        """
        Retrieves the AWS CloudWatch Log Group name after validating its existence.
    
        Args:
            resource (dict): The resource block from Terraform.
    
        Returns:
            str: The AWS CloudWatch Log Group name if it exists, otherwise None.
        """
        try:
            log_group_name = resource['change']['after']['name']
            
            # Check if the log group exists
            response = self.logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
            log_groups = response.get("logGroups", [])
    
            for log_group in log_groups:
                if log_group.get("logGroupName") == log_group_name:
                    return log_group_name
    
            # If log group is not found
            self.logger.error(f"CloudWatch Log Group '{log_group_name}' not found")
            return None
    
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except boto3.exceptions.Boto3Error as e:
            self.logger.error(f"Failed to validate CloudWatch Log Group: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
    
        return None

    #def aws_cloudwatch_event_rule(self, resource):
    #    return f"{resource['change']['after']['name']}"

    def aws_cloudwatch_event_rule(self, resource):
        """
        Retrieves the AWS CloudWatch Event Rule name after validating its existence.
    
        Args:
            resource (dict): The resource block from Terraform.
    
        Returns:
            str: The AWS CloudWatch Event Rule name if it exists, otherwise None.
        """
        try:
            rule_name = resource['change']['after']['name']
            
            # Create AWS Events client
            client = boto3.client('events')
    
            # Check if the event rule exists
            response = self.events_client.list_rules(NamePrefix=rule_name)
            rules = response.get("Rules", [])
    
            for rule in rules:
                if rule.get("Name") == rule_name:
                    return rule_name
    
            # If event rule is not found
            self.logger.error(f"CloudWatch Event Rule '{rule_name}' not found")
            return None
    
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except boto3.exceptions.Boto3Error as e:
            self.logger.error(f"Failed to validate CloudWatch Event Rule: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
    
        return None

    def aws_cloudwatch_log_metric_filter(self, resource):
        """
        Retrieves the AWS CloudWatch Log Metric Filter after validating its existence.
    
        Args:
            resource (dict): The resource block from Terraform.
    
        Returns:
            str: The AWS CloudWatch Log Metric Filter identifier if it exists, otherwise None.
        """
        try:
            name = resource['change']['after']['name']
            log_group_name = resource['change']['after']['log_group_name']
    
            # Check if the log metric filter exists
            response = self.logs_client.describe_metric_filters(logGroupName=log_group_name, filterNamePrefix=name)
            metric_filters = response.get("metricFilters", [])
    
            for metric_filter in metric_filters:
                if metric_filter.get("filterName") == name:
                    return f"{log_group_name}:{name}"
    
            # If metric filter is not found
            self.logger.error(f"CloudWatch Log Metric Filter '{name}' not found in log group '{log_group_name}'")
            return None
    
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except boto3.exceptions.Boto3Error as e:
            self.logger.error(f"Failed to validate CloudWatch Log Metric Filter: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
    
        return None
    
    def aws_cloudwatch_query_definition(self, resource, sessions):
        name = f"{resource['change']['after']['name']}"
        """
        Retrieves the ID of an AWS CloudWatch Logs Query Definition by its name.
    
        :param query_definition_name: The name of the CloudWatch Logs Query Definition.
        :return: The ID of the Query Definition, or None if not found.
        """
        try:
            # List all query definitions
            response =  self.logs_client.describe_query_definitions(queryDefinitionNamePrefix=name)
            for item in response["queryDefinitions"]:
                if item['name'] == name:
                    return f"arn:aws:logs:{self.region}:{self.account_id}:query-definition:{item['queryDefinitionId']}"
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
        return None
