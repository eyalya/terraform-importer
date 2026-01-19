import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
from terraform_importer.providers.aws.aws_services.base import BaseAWSService


class ConcreteAWSService(BaseAWSService):
    """Concrete implementation for testing BaseAWSService"""
    def get_resource_list(self):
        return ["test_resource"]


class TestBaseAWSService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_client = MagicMock()
        self.mock_session.client.return_value = self.mock_client
        self.service = ConcreteAWSService(self.mock_session)

    def test_init(self):
        """Test BaseAWSService initialization"""
        self.assertEqual(self.service.session, self.mock_session)
        self.assertIsNotNone(self.service.logger)

    def test_get_client(self):
        """Test get_client method"""
        client = self.service.get_client("ec2")
        self.mock_session.client.assert_called_once_with("ec2")
        self.assertEqual(client, self.mock_client)

    def test_get_resource_list(self):
        """Test get_resource_list returns correct list"""
        resources = self.service.get_resource_list()
        self.assertEqual(resources, ["test_resource"])

    def test_get_id_with_existing_method(self):
        """Test get_id method when resource method exists"""
        mock_resource = {"change": {"after": {"name": "test"}}}
        self.service.test_resource = Mock(return_value="test-id")
        
        result = self.service.get_id("test_resource", mock_resource)
        
        self.assertEqual(result, "test-id")
        self.service.test_resource.assert_called_once_with(mock_resource)

    def test_get_id_without_method(self):
        """Test get_id method when resource method doesn't exist"""
        mock_resource = {"change": {"after": {"name": "test"}}}
        
        result = self.service.get_id("non_existent_resource", mock_resource)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
