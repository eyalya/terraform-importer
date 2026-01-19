import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
from terraform_importer.providers.aws.aws_services.apigateway import APIGatewayService


class TestAPIGatewayService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_client = MagicMock()
        self.mock_session.client.return_value = self.mock_client
        self.service = APIGatewayService(self.mock_session)
        # Mock the exceptions attribute
        self.service.client.exceptions = MagicMock()
        self.service.client.exceptions.NotFoundException = type(
            'NotFoundException', (Exception,), {}
        )

    def test_init(self):
        """Test APIGatewayService initialization"""
        self.assertEqual(self.service.session, self.mock_session)
        self.mock_session.client.assert_called_with("apigateway")

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = [
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
        self.assertEqual(resources, expected_resources)

    def test_aws_api_gateway_rest_api_by_id(self):
        """Test aws_api_gateway_rest_api with ID"""
        resource = {
            "change": {
                "after": {
                    "id": "abc123",
                    "name": "test-api"
                }
            }
        }
        self.mock_client.get_rest_api.return_value = {
            "id": "abc123",
            "name": "test-api"
        }
        
        result = self.service.aws_api_gateway_rest_api(resource)
        
        self.assertEqual(result, "abc123")

    def test_aws_api_gateway_rest_api_by_name(self):
        """Test aws_api_gateway_rest_api with name"""
        resource = {
            "change": {
                "after": {
                    "name": "test-api"
                }
            }
        }
        self.mock_client.get_rest_apis.return_value = {
            "items": [{"id": "abc123", "name": "test-api"}]
        }
        
        result = self.service.aws_api_gateway_rest_api(resource)
        
        self.assertEqual(result, "abc123")

    def test_aws_api_gateway_rest_api_not_found(self):
        """Test aws_api_gateway_rest_api when API doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-api"
                }
            }
        }
        self.mock_client.get_rest_apis.return_value = {
            "items": []
        }
        
        result = self.service.aws_api_gateway_rest_api(resource)
        
        self.assertIsNone(result)

    def test_aws_api_gateway_resource_by_id(self):
        """Test aws_api_gateway_resource with ID"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123",
                    "id": "def456"
                }
            }
        }
        self.mock_client.get_resource.return_value = {
            "id": "def456"
        }
        
        result = self.service.aws_api_gateway_resource(resource)
        
        self.assertEqual(result, "abc123/def456")

    def test_aws_api_gateway_resource_by_path(self):
        """Test aws_api_gateway_resource with path"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123",
                    "path": "/test"
                }
            }
        }
        self.mock_client.get_resources.return_value = {
            "items": [{"id": "def456", "path": "/test"}]
        }
        
        result = self.service.aws_api_gateway_resource(resource)
        
        self.assertEqual(result, "abc123/def456")

    def test_aws_api_gateway_method_success(self):
        """Test aws_api_gateway_method with successful response"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123",
                    "resource_id": "def456",
                    "http_method": "GET"
                }
            }
        }
        self.mock_client.get_method.return_value = {
            "httpMethod": "GET"
        }
        
        result = self.service.aws_api_gateway_method(resource)
        
        self.assertEqual(result, "abc123/def456/GET")

    def test_aws_api_gateway_method_not_found(self):
        """Test aws_api_gateway_method when method doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123",
                    "resource_id": "def456",
                    "http_method": "GET"
                }
            }
        }
        self.mock_client.get_method.side_effect = self.service.client.exceptions.NotFoundException()
        
        result = self.service.aws_api_gateway_method(resource)
        
        self.assertIsNone(result)

    def test_aws_api_gateway_integration_success(self):
        """Test aws_api_gateway_integration with successful response"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123",
                    "resource_id": "def456",
                    "http_method": "GET"
                }
            }
        }
        self.mock_client.get_integration.return_value = {
            "type": "HTTP"
        }
        
        result = self.service.aws_api_gateway_integration(resource)
        
        self.assertEqual(result, "abc123/def456/GET")

    def test_aws_api_gateway_integration_not_found(self):
        """Test aws_api_gateway_integration when integration doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123",
                    "resource_id": "def456",
                    "http_method": "GET"
                }
            }
        }
        self.mock_client.get_integration.side_effect = self.service.client.exceptions.NotFoundException()
        
        result = self.service.aws_api_gateway_integration(resource)
        
        self.assertIsNone(result)

    def test_aws_api_gateway_deployment_by_id(self):
        """Test aws_api_gateway_deployment with ID"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123",
                    "id": "dep123"
                }
            }
        }
        self.mock_client.get_deployment.return_value = {
            "id": "dep123"
        }
        
        result = self.service.aws_api_gateway_deployment(resource)
        
        self.assertEqual(result, "abc123/dep123")

    def test_aws_api_gateway_deployment_latest(self):
        """Test aws_api_gateway_deployment without ID (gets latest)"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123"
                }
            }
        }
        self.mock_client.get_deployments.return_value = {
            "items": [{"id": "dep123"}]
        }
        
        result = self.service.aws_api_gateway_deployment(resource)
        
        self.assertEqual(result, "abc123/dep123")

    def test_aws_api_gateway_stage_success(self):
        """Test aws_api_gateway_stage with successful response"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123",
                    "stage_name": "prod"
                }
            }
        }
        self.mock_client.get_stage.return_value = {
            "stageName": "prod"
        }
        
        result = self.service.aws_api_gateway_stage(resource)
        
        self.assertEqual(result, "abc123/prod")

    def test_aws_api_gateway_stage_not_found(self):
        """Test aws_api_gateway_stage when stage doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123",
                    "stage_name": "prod"
                }
            }
        }
        self.mock_client.get_stage.side_effect = self.service.client.exceptions.NotFoundException()
        
        result = self.service.aws_api_gateway_stage(resource)
        
        self.assertIsNone(result)

    def test_aws_api_gateway_api_key_success(self):
        """Test aws_api_gateway_api_key with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-key"
                }
            }
        }
        self.mock_client.get_api_keys.return_value = {
            "items": [{"id": "key123", "name": "test-key"}]
        }
        
        result = self.service.aws_api_gateway_api_key(resource)
        
        self.assertEqual(result, "key123")

    def test_aws_api_gateway_api_key_not_found(self):
        """Test aws_api_gateway_api_key when key doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-key"
                }
            }
        }
        self.mock_client.get_api_keys.return_value = {
            "items": []
        }
        
        result = self.service.aws_api_gateway_api_key(resource)
        
        self.assertIsNone(result)

    def test_aws_api_gateway_usage_plan_success(self):
        """Test aws_api_gateway_usage_plan with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-plan"
                }
            }
        }
        self.mock_client.get_usage_plans.return_value = {
            "items": [{"id": "plan123", "name": "test-plan"}]
        }
        
        result = self.service.aws_api_gateway_usage_plan(resource)
        
        self.assertEqual(result, "plan123")

    def test_aws_api_gateway_authorizer_success(self):
        """Test aws_api_gateway_authorizer with successful response"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123",
                    "name": "test-authorizer"
                }
            }
        }
        self.mock_client.get_authorizers.return_value = {
            "items": [{"id": "auth123", "name": "test-authorizer"}]
        }
        
        result = self.service.aws_api_gateway_authorizer(resource)
        
        self.assertEqual(result, "abc123/auth123")

    def test_aws_api_gateway_method_response_success(self):
        """Test aws_api_gateway_method_response with successful response"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123",
                    "resource_id": "def456",
                    "http_method": "GET",
                    "status_code": "200"
                }
            }
        }
        self.mock_client.get_method_response.return_value = {
            "statusCode": "200"
        }
        
        result = self.service.aws_api_gateway_method_response(resource)
        
        self.assertEqual(result, "abc123/def456/GET/200")

    def test_aws_api_gateway_integration_response_success(self):
        """Test aws_api_gateway_integration_response with successful response"""
        resource = {
            "change": {
                "after": {
                    "rest_api_id": "abc123",
                    "resource_id": "def456",
                    "http_method": "GET",
                    "status_code": "200"
                }
            }
        }
        self.mock_client.get_integration_response.return_value = {
            "statusCode": "200"
        }
        
        result = self.service.aws_api_gateway_integration_response(resource)
        
        self.assertEqual(result, "abc123/def456/GET/200")

    def test_aws_api_gateway_rest_api_missing_fields(self):
        """Test aws_api_gateway_rest_api with missing fields"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_api_gateway_rest_api(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_api_by_id(self):
        """Test aws_apigatewayv2_api with ID"""
        resource = {
            "change": {
                "after": {
                    "id": "api123",
                    "name": "test-v2-api"
                }
            }
        }
        self.mock_client.get_api.return_value = {
            "ApiId": "api123",
            "Name": "test-v2-api"
        }
        
        result = self.service.aws_apigatewayv2_api(resource)
        
        self.assertEqual(result, "api123")

    def test_aws_apigatewayv2_api_by_name(self):
        """Test aws_apigatewayv2_api with name"""
        resource = {
            "change": {
                "after": {
                    "name": "test-v2-api"
                }
            }
        }
        self.mock_client.get_apis.return_value = {
            "Items": [{"ApiId": "api123", "Name": "test-v2-api"}]
        }
        
        result = self.service.aws_apigatewayv2_api(resource)
        
        self.assertEqual(result, "api123")

    def test_aws_apigatewayv2_api_not_found(self):
        """Test aws_apigatewayv2_api when API doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-v2-api"
                }
            }
        }
        self.mock_client.get_apis.return_value = {
            "Items": []
        }
        
        result = self.service.aws_apigatewayv2_api(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_api_missing_fields(self):
        """Test aws_apigatewayv2_api with missing id and name"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_apigatewayv2_api(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_api_client_error(self):
        """Test aws_apigatewayv2_api with ClientError"""
        resource = {
            "change": {
                "after": {
                    "name": "test-v2-api"
                }
            }
        }
        self.mock_client.get_apis.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "UnauthorizedOperation"}}, "GetApis"
        )
        
        result = self.service.aws_apigatewayv2_api(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_api_key_error(self):
        """Test aws_apigatewayv2_api with KeyError"""
        resource = {
            "change": {}
        }
        
        result = self.service.aws_apigatewayv2_api(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_api_multiple_apis(self):
        """Test aws_apigatewayv2_api with multiple APIs, finding the correct one"""
        resource = {
            "change": {
                "after": {
                    "name": "test-v2-api"
                }
            }
        }
        self.mock_client.get_apis.return_value = {
            "Items": [
                {"ApiId": "api123", "Name": "other-api"},
                {"ApiId": "api456", "Name": "test-v2-api"},
                {"ApiId": "api789", "Name": "another-api"}
            ]
        }
        
        result = self.service.aws_apigatewayv2_api(resource)
        
        self.assertEqual(result, "api456")

    # Tests for aws_apigatewayv2_authorizer
    def test_aws_apigatewayv2_authorizer_by_id(self):
        """Test aws_apigatewayv2_authorizer with ID"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "id": "auth456"
                }
            }
        }
        self.mock_client.get_authorizer.return_value = {
            "AuthorizerId": "auth456",
            "Name": "test-authorizer"
        }
        
        result = self.service.aws_apigatewayv2_authorizer(resource)
        
        self.assertEqual(result, "api123/auth456")

    def test_aws_apigatewayv2_authorizer_by_name(self):
        """Test aws_apigatewayv2_authorizer with name"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "name": "test-authorizer"
                }
            }
        }
        self.mock_client.get_authorizers.return_value = {
            "Items": [{"AuthorizerId": "auth456", "Name": "test-authorizer"}]
        }
        
        result = self.service.aws_apigatewayv2_authorizer(resource)
        
        self.assertEqual(result, "api123/auth456")

    def test_aws_apigatewayv2_authorizer_not_found_by_id(self):
        """Test aws_apigatewayv2_authorizer when authorizer ID doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "id": "auth456"
                }
            }
        }
        self.mock_client.get_authorizer.side_effect = self.service.client.exceptions.NotFoundException()
        
        result = self.service.aws_apigatewayv2_authorizer(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_authorizer_not_found_by_name(self):
        """Test aws_apigatewayv2_authorizer when authorizer name doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "name": "test-authorizer"
                }
            }
        }
        self.mock_client.get_authorizers.return_value = {
            "Items": []
        }
        
        result = self.service.aws_apigatewayv2_authorizer(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_authorizer_missing_api_id(self):
        """Test aws_apigatewayv2_authorizer with missing api_id"""
        resource = {
            "change": {
                "after": {
                    "name": "test-authorizer"
                }
            }
        }
        
        result = self.service.aws_apigatewayv2_authorizer(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_authorizer_missing_id_and_name(self):
        """Test aws_apigatewayv2_authorizer with missing id and name"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123"
                }
            }
        }
        
        result = self.service.aws_apigatewayv2_authorizer(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_authorizer_client_error(self):
        """Test aws_apigatewayv2_authorizer with ClientError"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "name": "test-authorizer"
                }
            }
        }
        self.mock_client.get_authorizers.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "UnauthorizedOperation"}}, "GetAuthorizers"
        )
        
        result = self.service.aws_apigatewayv2_authorizer(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_authorizer_key_error(self):
        """Test aws_apigatewayv2_authorizer with KeyError"""
        resource = {
            "change": {}
        }
        
        result = self.service.aws_apigatewayv2_authorizer(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_authorizer_multiple_authorizers(self):
        """Test aws_apigatewayv2_authorizer with multiple authorizers, finding the correct one"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "name": "test-authorizer"
                }
            }
        }
        self.mock_client.get_authorizers.return_value = {
            "Items": [
                {"AuthorizerId": "auth123", "Name": "other-authorizer"},
                {"AuthorizerId": "auth456", "Name": "test-authorizer"},
                {"AuthorizerId": "auth789", "Name": "another-authorizer"}
            ]
        }
        
        result = self.service.aws_apigatewayv2_authorizer(resource)
        
        self.assertEqual(result, "api123/auth456")

    # Tests for aws_apigatewayv2_api_mapping
    def test_aws_apigatewayv2_api_mapping_by_id(self):
        """Test aws_apigatewayv2_api_mapping with ID"""
        resource = {
            "change": {
                "after": {
                    "id": "mapping123",
                    "domain_name": "api.example.com"
                }
            }
        }
        self.mock_client.get_api_mapping.return_value = {
            "ApiMappingId": "mapping123",
            "DomainName": "api.example.com"
        }
        
        result = self.service.aws_apigatewayv2_api_mapping(resource)
        
        self.assertEqual(result, "mapping123/api.example.com")

    def test_aws_apigatewayv2_api_mapping_by_api_id(self):
        """Test aws_apigatewayv2_api_mapping with api_id"""
        resource = {
            "change": {
                "after": {
                    "domain_name": "api.example.com",
                    "api_id": "api123"
                }
            }
        }
        self.mock_client.get_api_mappings.return_value = {
            "Items": [{"ApiMappingId": "mapping123", "ApiId": "api123"}]
        }
        
        result = self.service.aws_apigatewayv2_api_mapping(resource)
        
        self.assertEqual(result, "mapping123/api.example.com")

    def test_aws_apigatewayv2_api_mapping_not_found(self):
        """Test aws_apigatewayv2_api_mapping when mapping doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "id": "mapping123",
                    "domain_name": "api.example.com"
                }
            }
        }
        self.mock_client.get_api_mapping.side_effect = self.service.client.exceptions.NotFoundException()
        
        result = self.service.aws_apigatewayv2_api_mapping(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_api_mapping_missing_domain_name(self):
        """Test aws_apigatewayv2_api_mapping with missing domain_name"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123"
                }
            }
        }
        
        result = self.service.aws_apigatewayv2_api_mapping(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_api_mapping_missing_id_and_api_id(self):
        """Test aws_apigatewayv2_api_mapping with missing id and api_id"""
        resource = {
            "change": {
                "after": {
                    "domain_name": "api.example.com"
                }
            }
        }
        
        result = self.service.aws_apigatewayv2_api_mapping(resource)
        
        self.assertIsNone(result)

    # Tests for aws_apigatewayv2_deployment
    def test_aws_apigatewayv2_deployment_by_id(self):
        """Test aws_apigatewayv2_deployment with ID"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "id": "dep456"
                }
            }
        }
        self.mock_client.get_deployment.return_value = {
            "DeploymentId": "dep456"
        }
        
        result = self.service.aws_apigatewayv2_deployment(resource)
        
        self.assertEqual(result, "api123/dep456")

    def test_aws_apigatewayv2_deployment_latest(self):
        """Test aws_apigatewayv2_deployment without ID (gets latest)"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123"
                }
            }
        }
        self.mock_client.get_deployments.return_value = {
            "Items": [{"DeploymentId": "dep456"}]
        }
        
        result = self.service.aws_apigatewayv2_deployment(resource)
        
        self.assertEqual(result, "api123/dep456")

    def test_aws_apigatewayv2_deployment_not_found(self):
        """Test aws_apigatewayv2_deployment when deployment doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "id": "dep456"
                }
            }
        }
        self.mock_client.get_deployment.side_effect = self.service.client.exceptions.NotFoundException()
        
        result = self.service.aws_apigatewayv2_deployment(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_deployment_missing_api_id(self):
        """Test aws_apigatewayv2_deployment with missing api_id"""
        resource = {
            "change": {
                "after": {
                    "id": "dep456"
                }
            }
        }
        
        result = self.service.aws_apigatewayv2_deployment(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_deployment_no_deployments(self):
        """Test aws_apigatewayv2_deployment when no deployments exist"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123"
                }
            }
        }
        self.mock_client.get_deployments.return_value = {
            "Items": []
        }
        
        result = self.service.aws_apigatewayv2_deployment(resource)
        
        self.assertIsNone(result)

    # Tests for aws_apigatewayv2_domain_name
    def test_aws_apigatewayv2_domain_name_success(self):
        """Test aws_apigatewayv2_domain_name with successful response"""
        resource = {
            "change": {
                "after": {
                    "domain_name": "api.example.com"
                }
            }
        }
        self.mock_client.get_domain_name.return_value = {
            "DomainName": "api.example.com"
        }
        
        result = self.service.aws_apigatewayv2_domain_name(resource)
        
        self.assertEqual(result, "api.example.com")

    def test_aws_apigatewayv2_domain_name_not_found(self):
        """Test aws_apigatewayv2_domain_name when domain doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "domain_name": "api.example.com"
                }
            }
        }
        self.mock_client.get_domain_name.side_effect = self.service.client.exceptions.NotFoundException()
        
        result = self.service.aws_apigatewayv2_domain_name(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_domain_name_missing_field(self):
        """Test aws_apigatewayv2_domain_name with missing domain_name"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_apigatewayv2_domain_name(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_domain_name_client_error(self):
        """Test aws_apigatewayv2_domain_name with ClientError"""
        resource = {
            "change": {
                "after": {
                    "domain_name": "api.example.com"
                }
            }
        }
        self.mock_client.get_domain_name.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "UnauthorizedOperation"}}, "GetDomainName"
        )
        
        result = self.service.aws_apigatewayv2_domain_name(resource)
        
        self.assertIsNone(result)

    # Tests for aws_apigatewayv2_integration
    def test_aws_apigatewayv2_integration_by_id(self):
        """Test aws_apigatewayv2_integration with ID"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "id": "int456"
                }
            }
        }
        self.mock_client.get_integration.return_value = {
            "IntegrationId": "int456"
        }
        
        result = self.service.aws_apigatewayv2_integration(resource)
        
        self.assertEqual(result, "api123/int456")

    def test_aws_apigatewayv2_integration_first_integration(self):
        """Test aws_apigatewayv2_integration without ID (gets first)"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123"
                }
            }
        }
        self.mock_client.get_integrations.return_value = {
            "Items": [{"IntegrationId": "int456"}]
        }
        
        result = self.service.aws_apigatewayv2_integration(resource)
        
        self.assertEqual(result, "api123/int456")

    def test_aws_apigatewayv2_integration_not_found(self):
        """Test aws_apigatewayv2_integration when integration doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "id": "int456"
                }
            }
        }
        self.mock_client.get_integration.side_effect = self.service.client.exceptions.NotFoundException()
        
        result = self.service.aws_apigatewayv2_integration(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_integration_missing_api_id(self):
        """Test aws_apigatewayv2_integration with missing api_id"""
        resource = {
            "change": {
                "after": {
                    "id": "int456"
                }
            }
        }
        
        result = self.service.aws_apigatewayv2_integration(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_integration_no_integrations(self):
        """Test aws_apigatewayv2_integration when no integrations exist"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123"
                }
            }
        }
        self.mock_client.get_integrations.return_value = {
            "Items": []
        }
        
        result = self.service.aws_apigatewayv2_integration(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_integration_client_error(self):
        """Test aws_apigatewayv2_integration with ClientError"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "id": "int456"
                }
            }
        }
        self.mock_client.get_integration.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "UnauthorizedOperation"}}, "GetIntegration"
        )
        
        result = self.service.aws_apigatewayv2_integration(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_integration_websocket_connect(self):
        """Test aws_apigatewayv2_integration with WebSocket connect integration_uri"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "integration_uri": "https://example.com/websocket/connect"
                }
            }
        }
        self.mock_client.get_routes.return_value = {
            "Items": [
                {"RouteKey": "$connect", "RouteId": "route123", "Target": "integrations/int456"},
                {"RouteKey": "$disconnect", "RouteId": "route789", "Target": "integrations/int999"}
            ]
        }
        self.mock_client.get_integration.return_value = {"IntegrationId": "int456"}
        
        result = self.service.aws_apigatewayv2_integration(resource)
        
        self.assertEqual(result, "api123/int456")

    def test_aws_apigatewayv2_integration_websocket_disconnect(self):
        """Test aws_apigatewayv2_integration with WebSocket disconnect integration_uri"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "integration_uri": "https://example.com/websocket/disconnect"
                }
            }
        }
        self.mock_client.get_routes.return_value = {
            "Items": [
                {"RouteKey": "$connect", "RouteId": "route123", "Target": "integrations/int456"},
                {"RouteKey": "$disconnect", "RouteId": "route789", "Target": "integrations/int999"}
            ]
        }
        self.mock_client.get_integration.return_value = {"IntegrationId": "int999"}
        
        result = self.service.aws_apigatewayv2_integration(resource)
        
        self.assertEqual(result, "api123/int999")

    def test_aws_apigatewayv2_integration_websocket_message(self):
        """Test aws_apigatewayv2_integration with WebSocket message integration_uri"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "integration_uri": "https://example.com/websocket/message"
                }
            }
        }
        self.mock_client.get_routes.return_value = {
            "Items": [
                {"RouteKey": "$connect", "RouteId": "route123", "Target": "integrations/int456"},
                {"RouteKey": "$default", "RouteId": "route555", "Target": "integrations/int777"}
            ]
        }
        self.mock_client.get_integration.return_value = {"IntegrationId": "int777"}
        
        result = self.service.aws_apigatewayv2_integration(resource)
        
        self.assertEqual(result, "api123/int777")

    def test_aws_apigatewayv2_integration_websocket_route_not_found(self):
        """Test aws_apigatewayv2_integration when WebSocket route doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "integration_uri": "https://example.com/websocket/connect"
                }
            }
        }
        self.mock_client.get_routes.return_value = {
            "Items": [
                {"RouteKey": "$disconnect", "RouteId": "route789", "Target": "integrations/int999"}
            ]
        }
        
        result = self.service.aws_apigatewayv2_integration(resource)
        
        self.assertIsNone(result)

    def test_get_websocket_route_key_from_uri_connect(self):
        """Test _get_websocket_route_key_from_uri with connect URI"""
        result = self.service._get_websocket_route_key_from_uri("https://example.com/websocket/connect")
        self.assertEqual(result, "$connect")

    def test_get_websocket_route_key_from_uri_disconnect(self):
        """Test _get_websocket_route_key_from_uri with disconnect URI"""
        result = self.service._get_websocket_route_key_from_uri("https://example.com/websocket/disconnect")
        self.assertEqual(result, "$disconnect")

    def test_get_websocket_route_key_from_uri_message(self):
        """Test _get_websocket_route_key_from_uri with message URI"""
        result = self.service._get_websocket_route_key_from_uri("https://example.com/websocket/message")
        self.assertEqual(result, "$default")

    def test_get_websocket_route_key_from_uri_default(self):
        """Test _get_websocket_route_key_from_uri with default URI"""
        result = self.service._get_websocket_route_key_from_uri("https://example.com/websocket/default")
        self.assertEqual(result, "$default")

    def test_get_websocket_route_key_from_uri_none(self):
        """Test _get_websocket_route_key_from_uri with None"""
        result = self.service._get_websocket_route_key_from_uri(None)
        self.assertIsNone(result)

    def test_get_websocket_route_key_from_uri_unknown(self):
        """Test _get_websocket_route_key_from_uri with unknown URI"""
        result = self.service._get_websocket_route_key_from_uri("https://example.com/api/endpoint")
        self.assertIsNone(result)

    # Tests for aws_apigatewayv2_integration_response
    def test_aws_apigatewayv2_integration_response_by_id(self):
        """Test aws_apigatewayv2_integration_response with ID"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "integration_id": "int456",
                    "id": "resp789"
                }
            }
        }
        self.mock_client.get_integration_response.return_value = {
            "IntegrationResponseId": "resp789"
        }
        
        result = self.service.aws_apigatewayv2_integration_response(resource)
        
        self.assertEqual(result, "api123/int456/resp789")

    def test_aws_apigatewayv2_integration_response_by_key(self):
        """Test aws_apigatewayv2_integration_response with integration_response_key"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "integration_id": "int456",
                    "integration_response_key": "/200"
                }
            }
        }
        self.mock_client.get_integration_responses.return_value = {
            "Items": [
                {"IntegrationResponseId": "resp111", "IntegrationResponseKey": "/default"},
                {"IntegrationResponseId": "resp789", "IntegrationResponseKey": "/200"}
            ]
        }
        
        result = self.service.aws_apigatewayv2_integration_response(resource)
        
        self.assertEqual(result, "api123/int456/resp789")

    def test_aws_apigatewayv2_integration_response_not_found(self):
        """Test aws_apigatewayv2_integration_response when response doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "integration_id": "int456",
                    "id": "resp789"
                }
            }
        }
        self.mock_client.get_integration_response.side_effect = self.service.client.exceptions.NotFoundException()
        
        result = self.service.aws_apigatewayv2_integration_response(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_integration_response_missing_fields(self):
        """Test aws_apigatewayv2_integration_response with missing required fields"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123"
                }
            }
        }
        
        result = self.service.aws_apigatewayv2_integration_response(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_integration_response_key_not_found(self):
        """Test aws_apigatewayv2_integration_response when key doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "integration_id": "int456",
                    "integration_response_key": "/404"
                }
            }
        }
        self.mock_client.get_integration_responses.return_value = {
            "Items": [
                {"IntegrationResponseId": "resp111", "IntegrationResponseKey": "/200"}
            ]
        }
        
        result = self.service.aws_apigatewayv2_integration_response(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_integration_response_missing_id_and_key(self):
        """Test aws_apigatewayv2_integration_response when neither id nor key provided"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "integration_id": "int456"
                }
            }
        }
        
        result = self.service.aws_apigatewayv2_integration_response(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_integration_response_client_error(self):
        """Test aws_apigatewayv2_integration_response with ClientError"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "integration_id": "int456",
                    "id": "resp789"
                }
            }
        }
        self.mock_client.get_integration_response.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "UnauthorizedOperation"}}, "GetIntegrationResponse"
        )
        
        result = self.service.aws_apigatewayv2_integration_response(resource)
        
        self.assertIsNone(result)

    # Tests for aws_apigatewayv2_route
    def test_aws_apigatewayv2_route_by_id(self):
        """Test aws_apigatewayv2_route with ID"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "id": "route456"
                }
            }
        }
        self.mock_client.get_route.return_value = {
            "RouteId": "route456"
        }
        
        result = self.service.aws_apigatewayv2_route(resource)
        
        self.assertEqual(result, "api123/route456")

    def test_aws_apigatewayv2_route_by_route_key(self):
        """Test aws_apigatewayv2_route with route_key"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "route_key": "GET /users"
                }
            }
        }
        self.mock_client.get_routes.return_value = {
            "Items": [{"RouteId": "route456", "RouteKey": "GET /users"}]
        }
        
        result = self.service.aws_apigatewayv2_route(resource)
        
        self.assertEqual(result, "api123/route456")

    def test_aws_apigatewayv2_route_not_found(self):
        """Test aws_apigatewayv2_route when route doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "id": "route456"
                }
            }
        }
        self.mock_client.get_route.side_effect = self.service.client.exceptions.NotFoundException()
        
        result = self.service.aws_apigatewayv2_route(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_route_not_found_by_key(self):
        """Test aws_apigatewayv2_route when route_key doesn't match"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "route_key": "GET /users"
                }
            }
        }
        self.mock_client.get_routes.return_value = {
            "Items": []
        }
        
        result = self.service.aws_apigatewayv2_route(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_route_missing_api_id(self):
        """Test aws_apigatewayv2_route with missing api_id"""
        resource = {
            "change": {
                "after": {
                    "id": "route456"
                }
            }
        }
        
        result = self.service.aws_apigatewayv2_route(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_route_missing_id_and_route_key(self):
        """Test aws_apigatewayv2_route with missing id and route_key"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123"
                }
            }
        }
        
        result = self.service.aws_apigatewayv2_route(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_route_client_error(self):
        """Test aws_apigatewayv2_route with ClientError"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "id": "route456"
                }
            }
        }
        self.mock_client.get_route.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "UnauthorizedOperation"}}, "GetRoute"
        )
        
        result = self.service.aws_apigatewayv2_route(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_route_multiple_routes(self):
        """Test aws_apigatewayv2_route with multiple routes, finding the correct one"""
        resource = {
            "change": {
                "after": {
                    "api_id": "api123",
                    "route_key": "GET /users"
                }
            }
        }
        self.mock_client.get_routes.return_value = {
            "Items": [
                {"RouteId": "route111", "RouteKey": "POST /users"},
                {"RouteId": "route456", "RouteKey": "GET /users"},
                {"RouteId": "route789", "RouteKey": "DELETE /users"}
            ]
        }
        
        result = self.service.aws_apigatewayv2_route(resource)
        
        self.assertEqual(result, "api123/route456")

    def test_aws_apigatewayv2_route_key_error(self):
        """Test aws_apigatewayv2_route with KeyError"""
        resource = {
            "change": {}
        }
        
        result = self.service.aws_apigatewayv2_route(resource)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
