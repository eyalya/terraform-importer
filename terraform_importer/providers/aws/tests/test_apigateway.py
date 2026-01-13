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
            "aws_api_gateway_integration_response"
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

    def test_aws_apigatewayv2_api_success(self):
        """Test aws_apigatewayv2_api with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-v2-api"
                }
            }
        }
        self.mock_client.get_apis.return_value = {
            "items": [{"id": "api123", "name": "test-v2-api"}]
        }
        
        result = self.service.aws_apigatewayv2_api(resource)
        
        self.assertEqual(result, "api123")
        self.mock_client.get_apis.assert_called_once()

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
            "items": []
        }
        
        result = self.service.aws_apigatewayv2_api(resource)
        
        self.assertIsNone(result)

    def test_aws_apigatewayv2_api_missing_name(self):
        """Test aws_apigatewayv2_api with missing name"""
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
            "items": [
                {"id": "api123", "name": "other-api"},
                {"id": "api456", "name": "test-v2-api"},
                {"id": "api789", "name": "another-api"}
            ]
        }
        
        result = self.service.aws_apigatewayv2_api(resource)
        
        self.assertEqual(result, "api456")


if __name__ == "__main__":
    unittest.main()
