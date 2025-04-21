from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import logging
from terraform_importer.providers.aws_services.base import BaseAWSService

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class CloudWatchService(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.logs_client = self.get_client("logs")
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

    def aws_cloudwatch_event_target(self, resource):
        try:
            rule_name = resource['change']['after']['rule']
            target_id = resource['change']['after']['target_id']
            
            # List targets for the rule
            response = self.logs_client.list_targets_by_rule(
                Rule=rule_name
            )
            
            # Check if target exists
            for target in response['Targets']:
                if target['Id'] == target_id:
                    return f"{rule_name}/{target_id}"
                
            global_logger.warning(f"CloudWatch event target {target_id} not found in rule {rule_name}")
            return None
        except Exception as e:
            global_logger.error(f"Error checking CloudWatch event target: {e}")
            return None

    def aws_cloudwatch_log_group(self, resource):
        try:
            log_group_name = resource['change']['after']['name']
            
            # Check if log group exists
            response = self.logs_client.describe_log_groups(
                logGroupNamePrefix=log_group_name
            )
            
            # Check exact match in returned log groups
            for log_group in response['logGroups']:
                if log_group['logGroupName'] == log_group_name:
                    return log_group_name
                
            global_logger.warning(f"CloudWatch log group {log_group_name} not found")
            return None
        except Exception as e:
            global_logger.error(f"cloudwatch_log_group: An error occurred: {e}")
            return None

    def aws_cloudwatch_metric_alarm(self, resource):
        try:
            alarm_name = resource['change']['after']['alarm_name']
            
            # Check if alarm exists
            response = self.cloudwatch_client.describe_alarms(
                AlarmName=alarm_name
            )
            
            # Check exact match in returned alarms
            for alarm in response['MetricAlarms']:
                if alarm['AlarmName'] == alarm_name:
                    return alarm_name
            global_logger.warning(f"CloudWatch metric alarm {alarm_name} not found")
            return None
        except Exception as e:
            global_logger.error(f"cloudwatch_metric_alarm: An error occurred: {e}")
            return None

    def aws_cloudwatch_event_rule(self, resource):
        try:
            rule_name = resource['change']['after']['name']
            
            # Check if rule exists
            response = self.cloudwatch_client.describe_rules(
                NamePrefix=rule_name
            )
            
            # Check exact match in returned rules
            for rule in response['Rules']:
                if rule['Name'] == rule_name:
                    return rule_name    
            global_logger.warning(f"CloudWatch event rule {rule_name} not found")
            return None
        except Exception as e:
            global_logger.error(f"cloudwatch_event_rule: An error occurred: {e}")
            return None

    def aws_cloudwatch_log_metric_filter(self, resource):
        try:
            name = resource['change']['after']['name']
            log_group_name = resource['change']['after']['log_group_name']
            
            # Check if metric filter exists
            response = self.logs_client.describe_metric_filters(
                logGroupName=log_group_name,
                filterNamePrefix=name
            )
            
            # Check exact match in returned filters
            for filter in response['metricFilters']:
                if filter['filterName'] == name:
                    return f"{log_group_name}:{name}"
                
            global_logger.warning(f"CloudWatch metric filter {name} not found in log group {log_group_name}")
            return None
        except Exception as e:
            global_logger.error(f"cloudwatch_log_metric_filter: An error occurred: {e}")
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
            global_logger.error(f"An error occurred: {e}")
        return None
