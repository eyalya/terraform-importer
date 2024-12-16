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

    def aws_cloudwatch_query_definition(self, resource):
        name = f"{resource['change']['after']['name']}"
        """
        Retrieves the ID of an AWS CloudWatch Logs Query Definition by its name.
        
        :param query_definition_name: The name of the CloudWatch Logs Query Definition.
        :return: The ID of the Query Definition, or None if not found.
        """
        try:
            # Use the DescribeInstances method with a filter for the Name tag
            response = self.logs_client.describe_instances(
                Filters=[
                    {
                        'Name': 'tag:Name',
                        'Values': [name]
                    }
                ]
            )
        
            # Collect instances from the response
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append(instance)
            
            return instance['InstanceId']
        except Exception as e:
        global_logger.error(f"An error occurred: {e}")

        return []

    def aws_cloudwatch_event_target(self, resource):
        return f"{resource['change']['after']['rule']}/{resource['change']['after']['target_id']}"

    def aws_cloudwatch_log_group(self, resource):
        try:
            return resource['change']['after']['name']
        except Exception as e:
            global_logger.error(f"An error occurred: {e}")
            return None

    def aws_cloudwatch_metric_alarm(self, resource):
        return f"{resource['change']['after']['alarm_name']}"

    def aws_cloudwatch_event_rule(self, resource):
        return f"{resource['change']['after']['name']}"

    def aws_cloudwatch_log_metric_filter(self resource):
        name = f"{resource['change']['after']['name']}"
        log_group_name = f"{resource['change']['after']['log_group_name']}"
        return  f"{log_group_name}:{name}"
    
    def aws_cloudwatch_query_definition(self, resource):
        name = f"{resource['change']['after']['name']}"
        """
        Retrieves the ID of an AWS CloudWatch Logs Query Definition by its name.
    
        :param query_definition_name: The name of the CloudWatch Logs Query Definition.
        :return: The ID of the Query Definition, or None if not found.
        """
        try:
            # List all query definitions
            response = logs_client.describe_query_definitions(queryDefinitionNamePrefix=name)
            for item in response["queryDefinitions"]:
                if item['name'] == name:
                    return item['queryDefinitionId']
        except Exception as e:
            global_logger.error(f"An error occurred: {e}")
        return None