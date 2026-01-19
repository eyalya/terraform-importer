import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
import importlib
lambda_module = importlib.import_module('terraform_importer.providers.aws.aws_services.lambda')
LambdaService = lambda_module.LambdaService


class TestLambdaService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_client = MagicMock()
        self.mock_session.client.return_value = self.mock_client
        self.service = LambdaService(self.mock_session)
        # Mock the exceptions attribute
        self.service.lambda_client.exceptions = MagicMock()
        self.service.lambda_client.exceptions.ResourceNotFoundException = type(
            'ResourceNotFoundException', (Exception,), {}
        )

    def test_init(self):
        """Test LambdaService initialization"""
        self.assertEqual(self.service.session, self.mock_session)
        self.mock_session.client.assert_called_with("lambda")

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = [
            "aws_lambda_function",
            "aws_lambda_function_url",
            "aws_lambda_function_event_invoke_config",
            "aws_lambda_permission"
        ]
        self.assertEqual(resources, expected_resources)

    def test_aws_lambda_function_success(self):
        """Test aws_lambda_function with successful response"""
        resource = {
            "change": {
                "after": {
                    "function_name": "test-function"
                }
            }
        }
        self.mock_client.get_function.return_value = {
            "Configuration": {"FunctionName": "test-function"}
        }
        
        result = self.service.aws_lambda_function(resource)
        
        self.assertEqual(result, "test-function")
        self.mock_client.get_function.assert_called_once_with(FunctionName="test-function")

    def test_aws_lambda_function_not_found(self):
        """Test aws_lambda_function when function doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "function_name": "test-function"
                }
            }
        }
        self.mock_client.get_function.side_effect = self.service.lambda_client.exceptions.ResourceNotFoundException()
        
        result = self.service.aws_lambda_function(resource)
        
        self.assertIsNone(result)

    def test_aws_lambda_function_missing_name(self):
        """Test aws_lambda_function with missing function_name"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_lambda_function(resource)
        
        self.assertIsNone(result)

    def test_aws_lambda_function_url_success(self):
        """Test aws_lambda_function_url with successful response"""
        resource = {
            "change": {
                "after": {
                    "function_name": "test-function"
                }
            }
        }
        self.mock_client.get_function_url_config.return_value = {
            "FunctionUrl": "https://test-function.lambda-url.us-east-1.on.aws/"
        }
        
        result = self.service.aws_lambda_function_url(resource)
        
        self.assertEqual(result, "test-function")

    def test_aws_lambda_function_url_not_found(self):
        """Test aws_lambda_function_url when URL doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "function_name": "test-function"
                }
            }
        }
        self.mock_client.get_function_url_config.side_effect = self.service.lambda_client.exceptions.ResourceNotFoundException()
        
        result = self.service.aws_lambda_function_url(resource)
        
        self.assertIsNone(result)

    def test_aws_lambda_function_event_invoke_config_success(self):
        """Test aws_lambda_function_event_invoke_config with successful response"""
        resource = {
            "change": {
                "after": {
                    "function_name": "test-function"
                }
            }
        }
        self.mock_client.get_function_event_invoke_config.return_value = {
            "FunctionName": "test-function"
        }
        
        result = self.service.aws_lambda_function_event_invoke_config(resource)
        
        self.assertEqual(result, "test-function")

    def test_aws_lambda_function_event_invoke_config_not_found(self):
        """Test aws_lambda_function_event_invoke_config when config doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "function_name": "test-function"
                }
            }
        }
        self.mock_client.get_function_event_invoke_config.side_effect = self.service.lambda_client.exceptions.ResourceNotFoundException()
        
        result = self.service.aws_lambda_function_event_invoke_config(resource)
        
        self.assertIsNone(result)

    def test_aws_lambda_permission_success(self):
        """Test aws_lambda_permission with successful response"""
        resource = {
            "change": {
                "after": {
                    "function_name": "test-function",
                    "statement_id": "test-statement"
                }
            }
        }
        self.mock_client.get_policy.return_value = {
            "Policy": '{"Statement": [{"Sid": "test-statement"}]}'
        }
        
        result = self.service.aws_lambda_permission(resource)
        
        self.assertEqual(result, "test-function/test-statement")

    def test_aws_lambda_permission_not_found(self):
        """Test aws_lambda_permission when permission doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "function_name": "test-function",
                    "statement_id": "test-statement"
                }
            }
        }
        self.mock_client.get_policy.return_value = {
            "Policy": '{"Statement": []}'
        }
        
        result = self.service.aws_lambda_permission(resource)
        
        self.assertIsNone(result)

    def test_aws_lambda_permission_missing_fields(self):
        """Test aws_lambda_permission with missing fields"""
        resource = {
            "change": {
                "after": {
                    "function_name": "test-function"
                }
            }
        }
        
        result = self.service.aws_lambda_permission(resource)
        
        self.assertIsNone(result)

    def test_aws_lambda_permission_client_error(self):
        """Test aws_lambda_permission with ClientError"""
        resource = {
            "change": {
                "after": {
                    "function_name": "test-function",
                    "statement_id": "test-statement"
                }
            }
        }
        self.mock_client.get_policy.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}}, "GetPolicy"
        )
        
        result = self.service.aws_lambda_permission(resource)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
