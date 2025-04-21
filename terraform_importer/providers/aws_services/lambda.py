from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import botocore
import logging
from terraform_importer.providers.aws_services.base import BaseAWSService

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class LambdaService(BaseAWSService):
    """
    Handles ECS-related resources (e.g., instances, AMIs).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.lambda_client = self.get_client("lambda")
        self._resources = [
            "aws_lambda_function",
            "aws_lambda_function_url",
            "aws_lambda_function_event_invoke_config",
            "aws_lambda_permission"
        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private EC2 resources list.
        Returns:
            list: A copy of the EC2 resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()

    def aws_lambda_function(self, resource):
        function_name = resource['change']['after'].get('function_name')
        if not function_name:
            global_logger.error("Missing Lambda function name.")
            return None
        try:
            self.lambda_client.get_function(FunctionName=function_name)
            return function_name
        except self.lambda_client.exceptions.ResourceNotFoundException:
            global_logger.error(f"Lambda function '{function_name}' not found.")
        return None

    def aws_lambda_function_url(self, resource):
        function_name = resource['change']['after'].get('function_name')
        if not function_name:
            global_logger.error("Missing Lambda function name.")
            return None
        try:
            self.lambda_client.get_function_url_config(FunctionName=function_name)
            return function_name
        except self.lambda_client.exceptions.ResourceNotFoundException:
            global_logger.error(f"Lambda function URL for '{function_name}' not found.")
        return None

    def aws_lambda_function_event_invoke_config(self, resource):
        function_name = resource['change']['after'].get('function_name')
        if not function_name:
            global_logger.error("Missing Lambda function name.")
            return None
        try:
            self.lambda_client.get_function_event_invoke_config(FunctionName=function_name)
            return function_name
        except self.lambda_client.exceptions.ResourceNotFoundException:
            global_logger.error(f"Event invoke config for Lambda function '{function_name}' not found.")
        return None

    def aws_lambda_permission(self, resource):
        function_name = resource['change']['after'].get('function_name')
        statement_id = resource['change']['after'].get('statement_id')
        if not function_name or not statement_id:
            global_logger.error("Missing function_name or statement_id.")
            return None
        try:
            policy_response = self.lambda_client.get_policy(FunctionName=function_name)
            policy_doc = policy_response.get('Policy')
            if policy_doc and statement_id in policy_doc:
                return f"{function_name}/{statement_id}"
            global_logger.error(f"Permission with statement_id '{statement_id}' not found in Lambda function '{function_name}'.")
        except self.lambda_client.exceptions.ResourceNotFoundException:
            global_logger.error(f"Lambda function '{function_name}' not found.")
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"Error retrieving policy for Lambda function '{function_name}': {e}")
        return None

    def aws_lambda_layer_version(self, resource):
        layer_name = resource['change']['after'].get('layer_name')
        if not layer_name:
            global_logger.error("Missing layer name.")
            return None
        try:
            response = self.lambda_client.list_layer_versions(LayerName=layer_name)
            if 'LayerVersions' in response and response['LayerVersions']:
                latest_layer = response['LayerVersions'][0]
                return latest_layer['LayerVersionArn']
            global_logger.error(f"No versions found for layer: {layer_name}")
        except self.lambda_client.exceptions.ResourceNotFoundException:
            global_logger.error(f"Layer '{layer_name}' not found.")
        except botocore.exceptions.ClientError as e:
            global_logger.error(f"ClientError while fetching layer versions: {e}")
        return None

    #def aws_lambda_function(self, resource):
    #    return resource['change']['after']['function_name']
    #
    #def aws_lambda_function_url(self, resource):
    #    return resource['change']['after']['function_name']
#
    #def aws_lambda_function_event_invoke_config(self, resource):
    #    return resource['change']['after']['function_name']
#
    #def aws_lambda_permission(self, resource):
    #    return f"{resource['change']['after']['function_name']}/{resource['change']['after']['statement_id']}"
#
    #def aws_lambda_layer_version(self, resource):
#
    #    layer_name = resource['change']['after']['layer_name']
#
    #    try:
    #        # List all versions of the specified Lambda Layer
    #        response = lambda_client.list_layer_versions(LayerName=layer_name)
    #        # Check if there are versions available
    #        if 'LayerVersions' in response and response['LayerVersions']:
    #            # Get the ARN of the latest version
    #            latest_layer = response['LayerVersions'][0]
    #            return latest_layer['LayerVersionArn']
    #        else:
    #            global_logger.error(f"No versions found for layer: {layer_name}")
    #            return None
    #
    #    except lambda_client.exceptions.ResourceNotFoundException:
    #        global_logger.error(f"Layer '{layer_name}' not found.")
    #        return None
