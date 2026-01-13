from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import boto3
import botocore
import logging
from terraform_importer.providers.aws.aws_services.base import BaseAWSService

class APIGatewayService(BaseAWSService):
    """
    Handles API Gateway-related resources (e.g., REST APIs, resources, methods, integrations).
    """
    def __init__(self, session: boto3.Session):
        super().__init__(session)
        self.logger = logging.getLogger(__name__)
        self.client = self.get_client("apigateway")
        self._resources = [
            "aws_api_gateway_rest_api",
            "aws_api_gateway_resource",
            "aws_api_gateway_method",
            "aws_api_gateway_integration",
            "aws_api_gateway_deployment",
            "aws_api_gateway_stage",
            "aws_api_gateway_api_key",
            "aws_api_gateway_usage_plan",
            "aws_api_gateway_authorizer",
            "aws_api_gateway_method_response",
            "aws_api_gateway_integration_response"
        ]

    def get_resource_list(self) -> List[str]:
        """
        Getter for the private API Gateway resources list.
        Returns:
            list: A copy of the API Gateway resources list.
        """
        # Return a copy to prevent external modification
        return self._resources.copy()

    def aws_api_gateway_rest_api(self, resource):
        """
        Retrieves the AWS API Gateway REST API ID after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway REST API ID if it exists, otherwise None.
        """
        try:
            api_id = resource['change']['after'].get('id')
            api_name = resource['change']['after'].get('name')
            
            if api_id:
                # If ID is provided, validate it directly
                try:
                    self.client.get_rest_api(restApiId=api_id)
                    return api_id
                except self.client.exceptions.NotFoundException:
                    self.logger.error(f"API Gateway REST API with ID '{api_id}' not found.")
                    return None
                except botocore.exceptions.ClientError as e:
                    self.logger.error(f"Error retrieving API Gateway REST API: {e}")
                    return None
            
            if api_name:
                # Search by name
                try:
                    apis = self.client.get_rest_apis()
                    for api in apis.get('items', []):
                        if api.get('name') == api_name:
                            return api['id']
                    self.logger.error(f"API Gateway REST API '{api_name}' not found.")
                except botocore.exceptions.ClientError as e:
                    self.logger.error(f"Error retrieving API Gateway REST APIs: {e}")
                    return None
            else:
                self.logger.error("Missing 'id' or 'name' in resource data")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway REST API: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_api_gateway_resource(self, resource):
        """
        Retrieves the AWS API Gateway Resource ID after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway Resource ID in format 'rest_api_id/resource_id' if it exists, otherwise None.
        """
        try:
            rest_api_id = resource['change']['after'].get('rest_api_id')
            resource_id = resource['change']['after'].get('id')
            path = resource['change']['after'].get('path')
            path_part = resource['change']['after'].get('path_part')
            
            if not rest_api_id:
                self.logger.error("Missing 'rest_api_id' in resource data")
                return None
            
            if resource_id:
                # If ID is provided, validate it directly
                try:
                    self.client.get_resource(restApiId=rest_api_id, resourceId=resource_id)
                    return f"{rest_api_id}/{resource_id}"
                except self.client.exceptions.NotFoundException:
                    self.logger.error(f"API Gateway Resource with ID '{resource_id}' not found.")
                    return None
            
            # Search by path or path_part
            if path or path_part:
                try:
                    resources = self.client.get_resources(restApiId=rest_api_id)
                    for res in resources.get('items', []):
                        if path and res.get('path') == path:
                            return f"{rest_api_id}/{res['id']}"
                        if path_part and res.get('pathPart') == path_part:
                            return f"{rest_api_id}/{res['id']}"
                    self.logger.error(f"API Gateway Resource with path '{path or path_part}' not found.")
                except botocore.exceptions.ClientError as e:
                    self.logger.error(f"Error retrieving API Gateway Resources: {e}")
                    return None
            else:
                self.logger.error("Missing 'id', 'path', or 'path_part' in resource data")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway Resource: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_api_gateway_method(self, resource):
        """
        Retrieves the AWS API Gateway Method identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway Method identifier in format 'rest_api_id/resource_id/http_method' if it exists, otherwise None.
        """
        try:
            rest_api_id = resource['change']['after'].get('rest_api_id')
            resource_id = resource['change']['after'].get('resource_id')
            http_method = resource['change']['after'].get('http_method')
            
            if not all([rest_api_id, resource_id, http_method]):
                self.logger.error("Missing required fields: 'rest_api_id', 'resource_id', or 'http_method'")
                return None
            
            try:
                self.client.get_method(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=http_method
                )
                return f"{rest_api_id}/{resource_id}/{http_method}"
            except self.client.exceptions.NotFoundException:
                self.logger.error(f"API Gateway Method '{http_method}' not found for resource '{resource_id}'.")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway Method: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_api_gateway_integration(self, resource):
        """
        Retrieves the AWS API Gateway Integration identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway Integration identifier in format 'rest_api_id/resource_id/http_method' if it exists, otherwise None.
        """
        try:
            rest_api_id = resource['change']['after'].get('rest_api_id')
            resource_id = resource['change']['after'].get('resource_id')
            http_method = resource['change']['after'].get('http_method')
            
            if not all([rest_api_id, resource_id, http_method]):
                self.logger.error("Missing required fields: 'rest_api_id', 'resource_id', or 'http_method'")
                return None
            
            try:
                self.client.get_integration(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=http_method
                )
                return f"{rest_api_id}/{resource_id}/{http_method}"
            except self.client.exceptions.NotFoundException:
                self.logger.error(f"API Gateway Integration not found for method '{http_method}' on resource '{resource_id}'.")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway Integration: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_api_gateway_deployment(self, resource):
        """
        Retrieves the AWS API Gateway Deployment ID after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway Deployment ID in format 'rest_api_id/deployment_id' if it exists, otherwise None.
        """
        try:
            rest_api_id = resource['change']['after'].get('rest_api_id')
            deployment_id = resource['change']['after'].get('id')
            
            if not rest_api_id:
                self.logger.error("Missing 'rest_api_id' in resource data")
                return None
            
            if deployment_id:
                # If ID is provided, validate it directly
                try:
                    self.client.get_deployment(restApiId=rest_api_id, deploymentId=deployment_id)
                    return f"{rest_api_id}/{deployment_id}"
                except self.client.exceptions.NotFoundException:
                    self.logger.error(f"API Gateway Deployment with ID '{deployment_id}' not found.")
                    return None
            else:
                # Get the latest deployment
                try:
                    deployments = self.client.get_deployments(restApiId=rest_api_id)
                    if deployments.get('items'):
                        latest_deployment = deployments['items'][0]
                        return f"{rest_api_id}/{latest_deployment['id']}"
                    self.logger.error(f"No deployments found for REST API '{rest_api_id}'.")
                except botocore.exceptions.ClientError as e:
                    self.logger.error(f"Error retrieving API Gateway Deployments: {e}")
                    return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway Deployment: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_api_gateway_stage(self, resource):
        """
        Retrieves the AWS API Gateway Stage identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway Stage identifier in format 'rest_api_id/stage_name' if it exists, otherwise None.
        """
        try:
            rest_api_id = resource['change']['after'].get('rest_api_id')
            stage_name = resource['change']['after'].get('stage_name')
            
            if not all([rest_api_id, stage_name]):
                self.logger.error("Missing required fields: 'rest_api_id' or 'stage_name'")
                return None
            
            try:
                self.client.get_stage(restApiId=rest_api_id, stageName=stage_name)
                return f"{rest_api_id}/{stage_name}"
            except self.client.exceptions.NotFoundException:
                self.logger.error(f"API Gateway Stage '{stage_name}' not found for REST API '{rest_api_id}'.")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway Stage: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_api_gateway_api_key(self, resource):
        """
        Retrieves the AWS API Gateway API Key ID after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway API Key ID if it exists, otherwise None.
        """
        try:
            api_key_id = resource['change']['after'].get('id')
            name = resource['change']['after'].get('name')
            
            if api_key_id:
                # If ID is provided, validate it directly
                try:
                    self.client.get_api_key(apiKey=api_key_id)
                    return api_key_id
                except self.client.exceptions.NotFoundException:
                    self.logger.error(f"API Gateway API Key with ID '{api_key_id}' not found.")
                    return None
            
            if name:
                # Search by name
                try:
                    api_keys = self.client.get_api_keys()
                    for key in api_keys.get('items', []):
                        if key.get('name') == name:
                            return key['id']
                    self.logger.error(f"API Gateway API Key '{name}' not found.")
                except botocore.exceptions.ClientError as e:
                    self.logger.error(f"Error retrieving API Gateway API Keys: {e}")
                    return None
            else:
                self.logger.error("Missing 'id' or 'name' in resource data")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway API Key: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_api_gateway_usage_plan(self, resource):
        """
        Retrieves the AWS API Gateway Usage Plan ID after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway Usage Plan ID if it exists, otherwise None.
        """
        try:
            usage_plan_id = resource['change']['after'].get('id')
            name = resource['change']['after'].get('name')
            
            if usage_plan_id:
                # If ID is provided, validate it directly
                try:
                    self.client.get_usage_plan(usagePlanId=usage_plan_id)
                    return usage_plan_id
                except self.client.exceptions.NotFoundException:
                    self.logger.error(f"API Gateway Usage Plan with ID '{usage_plan_id}' not found.")
                    return None
            
            if name:
                # Search by name
                try:
                    usage_plans = self.client.get_usage_plans()
                    for plan in usage_plans.get('items', []):
                        if plan.get('name') == name:
                            return plan['id']
                    self.logger.error(f"API Gateway Usage Plan '{name}' not found.")
                except botocore.exceptions.ClientError as e:
                    self.logger.error(f"Error retrieving API Gateway Usage Plans: {e}")
                    return None
            else:
                self.logger.error("Missing 'id' or 'name' in resource data")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway Usage Plan: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_api_gateway_authorizer(self, resource):
        """
        Retrieves the AWS API Gateway Authorizer identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway Authorizer identifier in format 'rest_api_id/authorizer_id' if it exists, otherwise None.
        """
        try:
            rest_api_id = resource['change']['after'].get('rest_api_id')
            authorizer_id = resource['change']['after'].get('id')
            name = resource['change']['after'].get('name')
            
            if not rest_api_id:
                self.logger.error("Missing 'rest_api_id' in resource data")
                return None
            
            if authorizer_id:
                # If ID is provided, validate it directly
                try:
                    self.client.get_authorizer(restApiId=rest_api_id, authorizerId=authorizer_id)
                    return f"{rest_api_id}/{authorizer_id}"
                except self.client.exceptions.NotFoundException:
                    self.logger.error(f"API Gateway Authorizer with ID '{authorizer_id}' not found.")
                    return None
            
            if name:
                # Search by name
                try:
                    authorizers = self.client.get_authorizers(restApiId=rest_api_id)
                    for auth in authorizers.get('items', []):
                        if auth.get('name') == name:
                            return f"{rest_api_id}/{auth['id']}"
                    self.logger.error(f"API Gateway Authorizer '{name}' not found.")
                except botocore.exceptions.ClientError as e:
                    self.logger.error(f"Error retrieving API Gateway Authorizers: {e}")
                    return None
            else:
                self.logger.error("Missing 'id' or 'name' in resource data")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway Authorizer: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_api_gateway_method_response(self, resource):
        """
        Retrieves the AWS API Gateway Method Response identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway Method Response identifier in format 'rest_api_id/resource_id/http_method/status_code' if it exists, otherwise None.
        """
        try:
            rest_api_id = resource['change']['after'].get('rest_api_id')
            resource_id = resource['change']['after'].get('resource_id')
            http_method = resource['change']['after'].get('http_method')
            status_code = resource['change']['after'].get('status_code')
            
            if not all([rest_api_id, resource_id, http_method, status_code]):
                self.logger.error("Missing required fields: 'rest_api_id', 'resource_id', 'http_method', or 'status_code'")
                return None
            
            try:
                self.client.get_method_response(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=http_method,
                    statusCode=status_code
                )
                return f"{rest_api_id}/{resource_id}/{http_method}/{status_code}"
            except self.client.exceptions.NotFoundException:
                self.logger.error(f"API Gateway Method Response with status code '{status_code}' not found for method '{http_method}' on resource '{resource_id}'.")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway Method Response: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_api_gateway_integration_response(self, resource):
        """
        Retrieves the AWS API Gateway Integration Response identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway Integration Response identifier in format 'rest_api_id/resource_id/http_method/status_code' if it exists, otherwise None.
        """
        try:
            rest_api_id = resource['change']['after'].get('rest_api_id')
            resource_id = resource['change']['after'].get('resource_id')
            http_method = resource['change']['after'].get('http_method')
            status_code = resource['change']['after'].get('status_code')
            
            if not all([rest_api_id, resource_id, http_method, status_code]):
                self.logger.error("Missing required fields: 'rest_api_id', 'resource_id', 'http_method', or 'status_code'")
                return None
            
            try:
                self.client.get_integration_response(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=http_method,
                    statusCode=status_code
                )
                return f"{rest_api_id}/{resource_id}/{http_method}/{status_code}"
            except self.client.exceptions.NotFoundException:
                self.logger.error(f"API Gateway Integration Response with status code '{status_code}' not found for method '{http_method}' on resource '{resource_id}'.")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway Integration Response: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None
    
    def aws_apigatewayv2_api(self, resource):
        """
        Retrieves the AWS API Gateway V2 API ID after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway V2 API ID if it exists, otherwise None.
        """
        try:
            name = resource['change']['after'].get('name')
            
            if name:
                # Search by name
                try:
                    apis = self.client.get_apis()
                    for api in apis.get('items', []):
                        if api.get('name') == name:
                            return api['id']
                    self.logger.error(f"API Gateway V2 API '{name}' not found.")
                except botocore.exceptions.ClientError as e:
                    self.logger.error(f"Error retrieving API Gateway V2 APIs: {e}")
                    return None
            else:
                self.logger.error("Missing 'name' in resource data")
                return None
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway V2 API: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None