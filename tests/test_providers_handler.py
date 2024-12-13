import unittest
from unittest.mock import Mock, patch
from typing import List, Dict
from terraform_importer.providers.base_provider import BaseProvider
from terraform_importer.handlers.providers_handler import ProvidersHandler


class TestProvidersHandler(unittest.TestCase):
    def setUp(self):
        """
        Set up mock providers for testing.
        """
        # Mock BaseProvider subclass
        self.mock_provider_aws = Mock(spec=BaseProvider)
        self.mock_provider_aws.get_id.return_value = "aws-id-123"

        # Initialize ProvidersHandler with mock providers
        self.providers = [self.mock_provider_aws]
        self.handler = ProvidersHandler(self.providers)

    def test_init(self):
        """
        Test initialization of ProvidersHandler.
        """
        # Ensure providers are correctly stored in a dictionary
        self.assertIn(type(self.mock_provider_aws).__name__, self.handler.providers)

    def test_validate_providers(self):
        """
        Test validate_providers to ensure all providers inherit from BaseProvider.
        """
        # Valid providers: should not raise any errors
        self.handler.validate_providers()

        # Add an invalid provider
        class InvalidProvider:
            pass

        invalid_providers = [InvalidProvider()]
        with self.assertRaises(TypeError):
            ProvidersHandler(invalid_providers)

    def test_get_resource_valid(self):
        """
        Test get_resource with a valid provider and resource block.
        """
        # Mock resource block
        resource_block = {
            "type": "Mock_instance",
            "address": "Mock_instance.my_instance"
        }

        # Test get_resource
        result = self.handler.get_resource("Mock_instance", resource_block)

        # Verify the result
        self.assertEqual(result, {"address": "Mock_instance.my_instance", "id": "aws-id-123"})
        self.mock_provider_aws.get_id.assert_called_once_with("Mock_instance", resource_block)

    def test_get_resource_no_id(self):
        """
        Test get_resource when the provider cannot fetch an ID.
        """
        # Mock provider returning None for get_id
        self.mock_provider_aws.get_id.return_value = None

        resource_block = {
            "type": "Mock_instance",
            "address": "Mock_instance.my_instance"
        }

        # Test get_resource
        result = self.handler.get_resource("Mock_instance", resource_block)

        # Verify the result is None
        self.assertIsNone(result)

    def test_run_all_resources(self):
        """
        Test run_all_resources to ensure all resources are processed correctly.
        """
        # Mock resource list
        resource_list = [
            {"type": "Mock_instance", "address": "Mock_instance.my_instance"},
            {"type": "Mock_ecs", "address": "Mock_ecs.my_ecs"},
        ]

        # Test run_all_resources
        results = self.handler.run_all_resources(resource_list)

        # Verify each resource was processed
        self.assertEqual(len(results), len(resource_list))


if __name__ == "__main__":
    unittest.main()
