import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock, patch
from terraform_importer.handlers.providers_handler import ProvidersHandler
from terraform_importer.providers.aws_provider import AWSProvider
from terraform_importer.providers.aws_services.aws_auth import AWSAuthHandler
from terraform_importer.providers.bitbucket_provider import BitbucketDfraustProvider
from terraform_importer.handlers.json_config_handler import JsonConfigHandler


class TestProvidersHandler(unittest.TestCase):
    
    def setUp(self):
        """Set up necessary mocks before each test."""
        # Mock dependencies
        self.mock_aws_provider = MagicMock(spec=AWSProvider)
        self.mock_bitbucket_provider = MagicMock(spec=BitbucketDfraustProvider)
        
        # Mock provider class mapping
        self.mock_providers_full_names = {
            "registry.terraform.io/hashicorp/aws": self.mock_aws_provider,
            "registry.terraform.io/hashicorp/bitbucket": self.mock_bitbucket_provider
        }

        # Create an invalid provider (not inheriting from BaseProvider)
        self.invalid_provider = MagicMock()

        # Example provider config
        self.provider_config = {
            "configuration": {
                "provider_config": {
                    "aws_provider": {
                        "full_name": "registry.terraform.io/hashicorp/aws",
                        "config_key": "value",
                    },
                    "bitbucket_provider": {
                        "full_name": "registry.terraform.io/hashicorp/bitbucket",
                        "config_key": "value"
                    }
                }
            },
            "variables": {}
        }

        with patch.object(JsonConfigHandler, "edit_provider_config", return_value=self.provider_config["configuration"]["provider_config"]), \
             patch.object(ProvidersHandler, "providers_full_names", self.mock_providers_full_names):
            # Create ProvidersHandler instance
            self.provider_handler = ProvidersHandler(self.provider_config)

        # create instances
        self.provider_handler.providers["aws_provider"] = self.mock_aws_provider
        self.provider_handler.providers["bitbucket_provider"] = self.mock_bitbucket_provider

        # Mock methods
        self.provider_handler.get_id = MagicMock()
    
    def test_init(self):
        """Test the __init__ function of ProvidersHandler."""

                # Assert provider initialization
        self.assertIn('aws_provider', self.provider_handler.providers)
        self.assertIn('bitbucket_provider', self.provider_handler.providers)
        self.mock_aws_provider.assert_called_once()
        self.mock_bitbucket_provider.assert_called_once()

    ########## validate_providers ########

    def test_validate_providers_success(self):
        """Test that validate_providers passes with valid providers."""
        self.provider_handler.validate_providers()  # Should not raise an error

    def test_validate_providers_failure(self):
        """Test that validate_providers raises TypeError for invalid provider."""
        self.provider_handler.providers["invalid_provider"] = self.invalid_provider  # Invalid
        with self.assertRaises(TypeError) as context:
            self.provider_handler.validate_providers()
        
        self.assertIn("Provider invalid_provider must inherit from BaseProvider.", str(context.exception))
    
    ########## run_all_resources ########

    def test_run_all_resources_success(self):
        """Test that run_all_resources correctly processes resources."""
        self.provider_handler.get_resource = MagicMock()
        # Sample input resource list
        resource_list = [
            {"type": "aws_instance", "name": "instance1"},
            {"type": "aws_s3_bucket", "name": "bucket1"},
            {"type": "aws_lambda", "name": "lambda1"},
        ]

        # Define mock return values for `get_resource`
        self.provider_handler.get_resource.side_effect = [
            {"address": "aws_instance.instance1", "id": "i-12345"},
            {"address": "aws_s3_bucket.bucket1", "id": "bucket-6789"},
            {"address": "aws_lambda.lambda1", "id": "lambda-abcde"},
        ]

        # Expected output
        expected_output = [
            {"address": "aws_instance.instance1", "id": "i-12345"},
            {"address": "aws_s3_bucket.bucket1", "id": "bucket-6789"},
            {"address": "aws_lambda.lambda1", "id": "lambda-abcde"},
        ]
        
        # Call the function
        result = self.provider_handler.run_all_resources(resource_list)

        # Validate results
        self.assertEqual(result, expected_output)
        self.assertEqual(self.provider_handler.get_resource.call_count, len(resource_list))

    def test_run_all_resources_with_none(self):
        """Test that run_all_resources handles None results from get_resource."""
        self.provider_handler.get_resource = MagicMock()
        resource_list = [
            {"type": "aws_instance", "name": "instance1"},
            {"type": "aws_s3_bucket", "name": "bucket1"},
        ]

        # `get_resource` returns None for one of the resources
        self.provider_handler.get_resource.side_effect = [
            {"address": "aws_instance.instance1", "id": "i-12345"},
            None  # Simulating a missing or unprocessable resource
        ]

        expected_output = [
            {"address": "aws_instance.instance1", "id": "i-12345"},
        ]  # The second resource is ignored

        result = self.provider_handler.run_all_resources(resource_list)

        # Validate results
        self.assertEqual(result, expected_output)
        self.assertEqual(self.provider_handler.get_resource.call_count, len(resource_list))

    def test_run_all_resources_empty_list(self):
        """Test that run_all_resources handles an empty resource list."""
        self.provider_handler.get_resource = MagicMock()
        resource_list = []  # Empty input list

        result = self.provider_handler.run_all_resources(resource_list)

        # Expect an empty result list
        self.assertEqual(result, [])
        self.provider_handler.get_resource.assert_not_called()

    ##########  get_resource ########

    def test_get_resource_valid_provider(self):
        """Test get_resource with a valid provider and resource."""
        self.mock_aws_provider.get_id.return_value = "i-123456"

        resource_block = {
            "provider": "aws_provider",
            "address": "aws_instance.example",
            "type": "aws_instance"
        }

        result = self.provider_handler.get_resource("aws_instance", resource_block)

        self.assertEqual(result, {"address": "aws_instance.example", "id": "i-123456"})
        self.mock_aws_provider.get_id.assert_called_once_with("aws_instance", resource_block)

    def test_get_resource_invalid_provider(self):
        """Test get_resource when the provider does not exist."""
        resource_block = {
            "provider": "nonexistent_provider",
            "address": "aws_instance.example",
            "type": "aws_instance"
        }


        with patch("terraform_importer.handlers.providers_handler.global_logger.warning") as mock_log:
            result = self.provider_handler.get_resource("aws_instance", resource_block)
            
            self.assertIsNone(result)
            mock_log.assert_called_once_with("Provider type nonexistent_provider doesnt exist")

    def test_get_resource_valid_provider_but_no_id(self):
        """Test get_resource when the provider exists but get_id returns None."""
        self.mock_aws_provider.get_id.return_value = None

        resource_block = {
            "provider": "aws_provider",
            "address": "aws_instance.example",
            "type": "aws_instance"
        }

        result = self.provider_handler.get_resource("aws_instance", resource_block)

        self.assertIsNone(result)
        self.mock_aws_provider.get_id.assert_called_once_with("aws_instance", resource_block)

    

if __name__ == '__main__':
    unittest.main()
