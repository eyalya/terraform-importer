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
            "aws_api_gateway_integration_response",
            "aws_apigatewayv2_api",
            "aws_apigatewayv2_authorizer",
            "aws_apigatewayv2_api_mapping",
            "aws_apigatewayv2_deployment",
            "aws_apigatewayv2_domain_name",
            "aws_apigatewayv2_integration",
            "aws_apigatewayv2_integration_response",
            "aws_apigatewayv2_route"
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
            api_id = resource['change']['after'].get('id')
            name = resource['change']['after'].get('name')
            
            # Get the apigatewayv2 client for HTTP/WebSocket APIs
            v2_client = self.get_client("apigatewayv2")
            
            if api_id:
                # If ID is provided, validate it directly
                try:
                    v2_client.get_api(ApiId=api_id)
                    return api_id
                except v2_client.exceptions.NotFoundException:
                    self.logger.error(f"API Gateway V2 API with ID '{api_id}' not found.")
                    return None
            
            if name:
                # Search by name
                try:
                    apis = v2_client.get_apis()
                    for api in apis.get('Items', []):
                        if api.get('Name') == name:
                            return api['ApiId']
                    self.logger.error(f"API Gateway V2 API '{name}' not found.")
                except botocore.exceptions.ClientError as e:
                    self.logger.error(f"Error retrieving API Gateway V2 APIs: {e}")
                    return None
            else:
                self.logger.error("Missing 'id' or 'name' in resource data")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway V2 API: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_apigatewayv2_authorizer(self, resource):
        """
        Retrieves the AWS API Gateway V2 Authorizer identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway V2 Authorizer identifier in format 'api_id/authorizer_id' if it exists, otherwise None.
        """
        try:
            api_id = resource['change']['after'].get('api_id')
            authorizer_id = resource['change']['after'].get('id')
            name = resource['change']['after'].get('name')
            
            if not api_id:
                self.logger.error("Missing 'api_id' in resource data")
                return None
            
            # Get the apigatewayv2 client for HTTP/WebSocket APIs
            v2_client = self.get_client("apigatewayv2")
            
            if authorizer_id:
                # If ID is provided, validate it directly
                try:
                    v2_client.get_authorizer(ApiId=api_id, AuthorizerId=authorizer_id)
                    return f"{api_id}/{authorizer_id}"
                except v2_client.exceptions.NotFoundException:
                    self.logger.error(f"API Gateway V2 Authorizer with ID '{authorizer_id}' not found.")
                    return None
            
            if name:
                # Search by name
                try:
                    authorizers = v2_client.get_authorizers(ApiId=api_id)
                    for auth in authorizers.get('Items', []):
                        if auth.get('Name') == name:
                            return f"{api_id}/{auth['AuthorizerId']}"
                    self.logger.error(f"API Gateway V2 Authorizer '{name}' not found.")
                except botocore.exceptions.ClientError as e:
                    self.logger.error(f"Error retrieving API Gateway V2 Authorizers: {e}")
                    return None
            else:
                self.logger.error("Missing 'id' or 'name' in resource data")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway V2 Authorizer: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_apigatewayv2_api_mapping(self, resource):
        """
        Retrieves the AWS API Gateway V2 API Mapping identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway V2 API Mapping identifier in format 'api_mapping_id/domain_name' if it exists, otherwise None.
        """
        try:
            api_mapping_id = resource['change']['after'].get('id')
            domain_name = resource['change']['after'].get('domain_name')
            api_id = resource['change']['after'].get('api_id')
            
            if not domain_name:
                self.logger.error("Missing 'domain_name' in resource data")
                return None
            
            # Get the apigatewayv2 client for HTTP/WebSocket APIs
            v2_client = self.get_client("apigatewayv2")
            
            if api_mapping_id:
                # If ID is provided, validate it directly
                try:
                    v2_client.get_api_mapping(ApiMappingId=api_mapping_id, DomainName=domain_name)
                    return f"{api_mapping_id}/{domain_name}"
                except v2_client.exceptions.NotFoundException:
                    self.logger.warning(f"API Gateway V2 API Mapping with ID '{api_mapping_id}' not found.")
                    return None
            
            if api_id:
                # Search by api_id
                try:
                    mappings = v2_client.get_api_mappings(DomainName=domain_name)
                    for mapping in mappings.get('Items', []):
                        if mapping.get('ApiId') == api_id:
                            return f"{mapping['ApiMappingId']}/{domain_name}"
                    self.logger.warning(f"API Gateway V2 API Mapping for API '{api_id}' not found on domain '{domain_name}'.")
                except botocore.exceptions.ClientError as e:
                    self.logger.warning(f"Error retrieving API Gateway V2 API Mappings: {e}")
                    return None
            else:
                self.logger.error("Missing 'id' or 'api_id' in resource data")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway V2 API Mapping: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_apigatewayv2_deployment(self, resource):
        """
        Retrieves the AWS API Gateway V2 Deployment identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway V2 Deployment identifier in format 'api_id/deployment_id' if it exists, otherwise None.
        """
        try:
            api_id = resource['change']['after'].get('api_id')
            deployment_id = resource['change']['after'].get('id')
            
            if not api_id:
                self.logger.error("Missing 'api_id' in resource data")
                return None
            
            # Get the apigatewayv2 client for HTTP/WebSocket APIs
            v2_client = self.get_client("apigatewayv2")
            
            if deployment_id:
                # If ID is provided, validate it directly
                try:
                    v2_client.get_deployment(ApiId=api_id, DeploymentId=deployment_id)
                    return f"{api_id}/{deployment_id}"
                except v2_client.exceptions.NotFoundException:
                    self.logger.warning(f"API Gateway V2 Deployment with ID '{deployment_id}' not found.")
                    return None
            else:
                # Get the latest deployment
                try:
                    deployments = v2_client.get_deployments(ApiId=api_id)
                    if deployments.get('Items'):
                        latest_deployment = deployments['Items'][0]
                        return f"{api_id}/{latest_deployment['DeploymentId']}"
                    self.logger.warning(f"No deployments found for API '{api_id}'.")
                except botocore.exceptions.ClientError as e:
                    self.logger.warning(f"Error retrieving API Gateway V2 Deployments: {e}")
                    return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway V2 Deployment: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_apigatewayv2_domain_name(self, resource):
        """
        Retrieves the AWS API Gateway V2 Domain Name after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway V2 Domain Name if it exists, otherwise None.
        """
        try:
            domain_name = resource['change']['after'].get('domain_name')
            
            if not domain_name:
                self.logger.error("Missing 'domain_name' in resource data")
                return None
            
            # Get the apigatewayv2 client for HTTP/WebSocket APIs
            v2_client = self.get_client("apigatewayv2")
            
            try:
                v2_client.get_domain_name(DomainName=domain_name)
                return domain_name
            except v2_client.exceptions.NotFoundException:
                self.logger.warning(f"API Gateway V2 Domain Name '{domain_name}' not found.")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway V2 Domain Name: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_apigatewayv2_integration(self, resource):
        """
        Retrieves the AWS API Gateway V2 Integration identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway V2 Integration identifier in format 'api_id/integration_id' if it exists, otherwise None.
        """
        try:
            api_id = resource['change']['after'].get('api_id')
            integration_id = resource['change']['after'].get('id')
            
            if not api_id:
                self.logger.error("Missing 'api_id' in resource data")
                return None
            
            # Get the apigatewayv2 client for HTTP/WebSocket APIs
            v2_client = self.get_client("apigatewayv2")
            
            if integration_id:
                # If ID is provided, validate it directly
                try:
                    v2_client.get_integration(ApiId=api_id, IntegrationId=integration_id)
                    return f"{api_id}/{integration_id}"
                except v2_client.exceptions.NotFoundException:
                    self.logger.warning(f"API Gateway V2 Integration with ID '{integration_id}' not found.")
                    return None
            else:
                # Get the first integration
                try:
                    integrations = v2_client.get_integrations(ApiId=api_id)
                    if integrations.get('Items'):
                        first_integration = integrations['Items'][0]
                        return f"{api_id}/{first_integration['IntegrationId']}"
                    self.logger.warning(f"No integrations found for API '{api_id}'.")
                except botocore.exceptions.ClientError as e:
                    self.logger.warning(f"Error retrieving API Gateway V2 Integrations: {e}")
                    return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway V2 Integration: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_apigatewayv2_integration_response(self, resource):
        """
        Retrieves the AWS API Gateway V2 Integration Response identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway V2 Integration Response identifier in format 'api_id/integration_id/integration_response_id' if it exists, otherwise None.
        """
        try:
            api_id = resource['change']['after'].get('api_id')
            integration_id = resource['change']['after'].get('integration_id')
            integration_response_id = resource['change']['after'].get('id')
            
            if not all([api_id, integration_id]):
                self.logger.error("Missing required fields: 'api_id' or 'integration_id'")
                return None
            
            # Get the apigatewayv2 client for HTTP/WebSocket APIs
            v2_client = self.get_client("apigatewayv2")
            
            if integration_response_id:
                # If ID is provided, validate it directly
                try:
                    v2_client.get_integration_response(
                        ApiId=api_id,
                        IntegrationId=integration_id,
                        IntegrationResponseId=integration_response_id
                    )
                    return f"{api_id}/{integration_id}/{integration_response_id}"
                except v2_client.exceptions.NotFoundException:
                    self.logger.warning(f"API Gateway V2 Integration Response with ID '{integration_response_id}' not found.")
                    return None
            else:
                # Get the first integration response
                try:
                    responses = v2_client.get_integration_responses(ApiId=api_id, IntegrationId=integration_id)
                    if responses.get('Items'):
                        first_response = responses['Items'][0]
                        return f"{api_id}/{integration_id}/{first_response['IntegrationResponseId']}"
                    self.logger.warning(f"No integration responses found for integration '{integration_id}'.")
                except botocore.exceptions.ClientError as e:
                    self.logger.warning(f"Error retrieving API Gateway V2 Integration Responses: {e}")
                    return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway V2 Integration Response: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None

    def aws_apigatewayv2_route(self, resource):
        """
        Retrieves the AWS API Gateway V2 Route identifier after validating its existence.
        
        Args:
            resource (dict): The resource block from Terraform.
        
        Returns:
            str: The AWS API Gateway V2 Route identifier in format 'api_id/route_id' if it exists, otherwise None.
        """
        try:
            api_id = resource['change']['after'].get('api_id')
            route_id = resource['change']['after'].get('id')
            route_key = resource['change']['after'].get('route_key')
            
            if not api_id:
                self.logger.error("Missing 'api_id' in resource data")
                return None
            
            # Get the apigatewayv2 client for HTTP/WebSocket APIs
            v2_client = self.get_client("apigatewayv2")
            
            if route_id:
                # If ID is provided, validate it directly
                try:
                    v2_client.get_route(ApiId=api_id, RouteId=route_id)
                    return f"{api_id}/{route_id}"
                except v2_client.exceptions.NotFoundException:
                    self.logger.warning(f"API Gateway V2 Route with ID '{route_id}' not found.")
                    return None
            
            if route_key:
                # Search by route_key
                try:
                    routes = v2_client.get_routes(ApiId=api_id)
                    for route in routes.get('Items', []):
                        if route.get('RouteKey') == route_key:
                            return f"{api_id}/{route['RouteId']}"
                    self.logger.warning(f"API Gateway V2 Route with key '{route_key}' not found.")
                except botocore.exceptions.ClientError as e:
                    self.logger.warning(f"Error retrieving API Gateway V2 Routes: {e}")
                    return None
            else:
                self.logger.error("Missing 'id' or 'route_key' in resource data")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing expected key in resource: {e}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"AWS ClientError while validating API Gateway V2 Route: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        
        return None