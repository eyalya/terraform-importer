import unittest
from unittest.mock import Mock, patch
from typing import List, Dict
import boto3

from terraform_importer.providers.aws_services.ec2 import BaseAWSService, EC2Service 


class TestBaseAWSService(unittest.TestCase):
    @patch("boto3.Session")
    def test_get_client(self, mock_session):
        # Mock the session and client
        mock_client = Mock()
        mock_session.return_value.client.return_value = mock_client

        # Create a concrete class for testing
        class TestService(BaseAWSService):
            def get_resource_list(self) -> List[str]:
                return []

        session = mock_session.return_value
        service = TestService(session)
        
        # Test the get_client method
        client = service.get_client("ec2")
        mock_session.return_value.client.assert_called_once_with("ec2")
        self.assertEqual(client, mock_client)

    def test_abstract_method_get_resource_list(self):
        # Ensure the abstract method cannot be instantiated without implementation
        class TestService(BaseAWSService):
            pass

        with self.assertRaises(TypeError):
            TestService(Mock())

    @patch("boto3.Session")
    def test_get_id(self, mock_session):
        # Create a concrete class for testing
        class TestService(BaseAWSService):
            def get_resource_list(self) -> List[str]:
                return []

            def example_resource(self, resource_block: Dict):
                return resource_block.get("id")

        session = mock_session.return_value
        service = TestService(session)

        # Test get_id with a valid resource type
        resource_block = {"id": "test-id"}
        self.assertEqual(service.get_id("example_resource", resource_block), "test-id")

        # Test get_id with an invalid resource type
        self.assertIsNone(service.get_id("invalid_resource", resource_block))
        # with self.assertLogs("global_logger", level="INFO") as log:
        #     self.assertIsNone(service.get_id("invalid_resource", resource_block))
        #     self.assertIn("No such resource_type: invalid_resource", log.output[0])


class TestEC2Service(unittest.TestCase):
    @patch("boto3.Session")
    def test_get_resource_list(self, mock_session):
        # Mock session
        session = mock_session.return_value

        # Initialize EC2Service
        ec2_service = EC2Service(session)

        # Test get_resource_list
        expected_resources = ["aws_security_group", "aws_security_group_rule"]
        self.assertEqual(ec2_service.get_resource_list(), expected_resources)

    @patch("boto3.Session")
    def test_aws_security_group(self, mock_session):
        # Mock session and EC2 client
        session = mock_session.return_value
        mock_client = Mock()
        session.client.return_value = mock_client

        # Set up the mock response
        mock_client.describe_security_groups.return_value = {
            "SecurityGroups": [{"GroupId": "sg-12345678"}]
        }

        # Initialize EC2Service
        ec2_service = EC2Service(session)

        # Test aws_security_group
        resource_block = {
            "change": {
                "after": {"tags": {"Name": "test-sg"}}
            }
        }
        group_id = ec2_service.aws_security_group(resource_block)
        self.assertEqual(group_id, "sg-12345678")

        # Ensure the client call was made correctly
        mock_client.describe_security_groups.assert_called_once_with(
            Filters=[{"Name": "tag:Name", "Values": ["test-sg"]}]
        )

    @patch("boto3.Session")
    def test_aws_security_group_no_groups(self, mock_session):
        # Mock session and EC2 client
        session = mock_session.return_value
        mock_client = Mock()
        session.client.return_value = mock_client

        # Set up the mock response with no SecurityGroups
        mock_client.describe_security_groups.return_value = {"SecurityGroups": []}

        # Initialize EC2Service
        ec2_service = EC2Service(session)

        # Test aws_security_group
        resource_block = {
            "change": {
                "after": {"tags": {"Name": "test-sg"}}
            }
        }
        group_id = ec2_service.aws_security_group(resource_block)
        self.assertIsNone(group_id)


if __name__ == "__main__":
    unittest.main()
