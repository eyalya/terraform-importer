import unittest
from unittest.mock import Mock, patch, call, MagicMock
from terraform_importer.providers.aws_services.base import BaseAWSService
from terraform_importer.providers.aws_provider import AWSProvider
import os
import json


class TestAWSProvider(unittest.TestCase):
    @patch("terraform_importer.providers.aws_provider.boto3.session.Session")
    @patch("terraform_importer.providers.aws_provider.AWSProvider.get_aws_service_subclasses")
    def test_init(self, mock_get_subclasses, mock_session):
        # Mock the boto3 session
        session_mock = mock_session.return_value
        session_mock.client = Mock()

        # Mock discovered subclasses
        mock_service_class = Mock(spec=BaseAWSService)
        mock_service_instance = Mock()
        mock_service_instance.get_resource_list.return_value = ["aws_instance"]
        mock_service_class.return_value = mock_service_instance
        mock_get_subclasses.return_value = [mock_service_class]

        # Initialize AWSProvider
        provider = AWSProvider()

        # Ensure session is initialized
        mock_session.assert_called_once_with(profile_name="cordio-payer")

        # Verify get_aws_service_subclasses was called
        mock_get_subclasses.assert_called_once_with(
            BaseAWSService, "terraform_importer/providers/aws_services"
        )

        # Verify _resources_dict is populated
        self.assertIn("aws_instance", provider._resources_dict)
        self.assertEqual(provider._resources_dict["aws_instance"], mock_service_instance)

    def test_add_to_resource_dict(self):
        # Mock a service instance
        mock_service_instance = Mock()
        mock_service_instance.get_resource_list.return_value = ["aws_instance"]

        # Create an AWSProvider and add to _resources_dict
        provider = AWSProvider()
        provider.add_to_resource_dict(mock_service_instance)

        # Verify the resource dictionary is updated
        self.assertIn("aws_instance", provider._resources_dict)
        self.assertEqual(provider._resources_dict["aws_instance"], mock_service_instance)

    def test_get_aws_service_subclasses(self):
       
        # Create an AWSProvider and call get_aws_service_subclasses
        provider = AWSProvider()
        subclasses = provider.get_aws_service_subclasses(BaseAWSService, "terraform_importer/providers/aws_services")
        self.assertGreater(len(subclasses), 1)

    @patch("terraform_importer.providers.aws_provider.AWSProvider.add_to_resource_dict")
    def test_get_id(self, mock_add_to_resource_dict):
        # Mock a service instance
        mock_service_instance = Mock()
        mock_service_instance.get_id.return_value = "sg-0d5a58d8d4ccc77b4"
        mock_service_instance.get_resource_list.return_value = ["aws_security_group"]

        # Create an AWSProvider and populate _resources_dict
        provider = AWSProvider()
        provider._resources_dict = {"aws_security_group": mock_service_instance}

        # Test get_id
        resource_block = {
            "address": "aws_security_group.algo_rds",
            "type": "aws_security_group",
            "name": "algo_rds",
            "change": {
                "actions": [
                    "create"
                ],
                "after": {
                    "description": "Created by RDS management console",
                    "egress": [],
                    "id": "sg-0d5a58d8d4ccc77b4",
                    "ingress": [
                        {
                            "cidr_blocks": [],
                            "description": "",
                            "from_port": 3306,
                            "ipv6_cidr_blocks": [],
                            "prefix_list_ids": [],
                            "protocol": "tcp",
                            "to_port": 3306
                        }
                    ],
                    "name": "algo-db-dev1-sg",
                    "name_prefix": "",
                    "owner_id": "891513744586",
                    "tags": {
                        "Environment": "dev1",
                        "Name": "Algo RDS connections - dev1"
                    },
                    "tags_all": {
                        "Environment": "dev1",
                        "Name": "Algo RDS connections - dev1"
                    },
                    "vpc_id": "vpc-010d24345a80f29eb"
                },
                
            }
        }
        result = provider.get_id("aws_security_group", resource_block)
        self.assertEqual(result, "sg-0d5a58d8d4ccc77b4")

        # Verify get_id is called on the service instance
        mock_service_instance.get_id.assert_called_once_with("aws_security_group", resource_block)


if __name__ == "__main__":
    unittest.main()
