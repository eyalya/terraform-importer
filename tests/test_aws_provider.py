import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import Mock, patch, call, MagicMock
from terraform_importer.providers.aws_services.base import BaseAWSService
from terraform_importer.providers.aws_provider import AWSProvider
from terraform_importer.providers.aws_services.aws_auth import AWSAuthHandler
import json

class TestAWSProviderInit(unittest.TestCase):
    def setUp(self):
        self.mock_auth_config = {"expressions":{"aws_access_key_id": "test", "aws_secret_access_key": "test"}}
        self.mock_auth_handler = MagicMock(spec=AWSAuthHandler)
        self.mock_auth_handler.get_session.return_value = {"session": "mock_session"}
    
    @patch("terraform_importer.providers.aws_provider.AWSAuthHandler", autospec=True)
    @patch("terraform_importer.providers.aws_provider.AWSProvider.get_aws_service_subclasses", return_value=[])
    def test_init(self, mock_get_aws_service_subclasses, mock_auth_handler_class):
        # Mock AWSAuthHandler instance
        mock_auth_handler_class.return_value = self.mock_auth_handler
        
        provider = AWSProvider(self.mock_auth_config)
        
        # Assertions
        mock_auth_handler_class.assert_called_once_with(self.mock_auth_config)
        self.assertEqual(provider.__name__, "aws")
        self.assertEqual(provider._sessions, {"session": "mock_session"})
        mock_get_aws_service_subclasses.assert_called_once()
        self.assertEqual(provider._resources_dict, {})
    
    @patch("terraform_importer.providers.aws_provider.AWSProvider.get_aws_service_subclasses", return_value=[])
    def test_add_to_resource_dict(self, mock_get_aws_service_subclasses):
        provider = AWSProvider(self.mock_auth_config)
        mock_service = MagicMock(spec=BaseAWSService)
        mock_service.get_resource_list.return_value = ["resource1", "resource2"]
        
        provider.add_to_resource_dict(mock_service)
        
        # Assertions
        self.assertIn("resource1", provider._resources_dict)
        self.assertIn("resource2", provider._resources_dict)
        self.assertEqual(provider._resources_dict["resource1"], mock_service)
        self.assertEqual(provider._resources_dict["resource2"], mock_service)

    #TODO: unit test for get_aws_service_subclasses , get_id   

if __name__ == "__main__":
    unittest.main()