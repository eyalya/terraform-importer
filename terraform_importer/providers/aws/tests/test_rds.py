import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
from terraform_importer.providers.aws.aws_services.rds import EC2Service as RDSService


class TestRDSService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_client = MagicMock()
        self.mock_session.client.return_value = self.mock_client
        self.service = RDSService(self.mock_session)
        # Mock the exceptions attribute
        self.service.client.exceptions = MagicMock()
        self.service.client.exceptions.DBInstanceNotFoundFault = type(
            'DBInstanceNotFoundFault', (Exception,), {}
        )
        self.service.client.exceptions.DBSubnetGroupNotFoundFault = type(
            'DBSubnetGroupNotFoundFault', (Exception,), {}
        )

    def test_init(self):
        """Test RDSService initialization"""
        self.assertEqual(self.service.session, self.mock_session)
        self.mock_session.client.assert_called_with("rds")

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = [
            "aws_db_instance",
            "aws_db_subnet_group"
        ]
        self.assertEqual(resources, expected_resources)

    def test_aws_db_instance_success(self):
        """Test aws_db_instance with successful response"""
        resource = {
            "change": {
                "after": {
                    "identifier": "test-db"
                }
            }
        }
        self.mock_client.describe_db_instances.return_value = {
            "DBInstances": [{"DBInstanceIdentifier": "test-db"}]
        }
        
        result = self.service.aws_db_instance(resource)
        
        self.assertEqual(result, "test-db")
        self.mock_client.describe_db_instances.assert_called_once_with(DBInstanceIdentifier="test-db")

    def test_aws_db_instance_not_found(self):
        """Test aws_db_instance when DB instance doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "identifier": "test-db"
                }
            }
        }
        self.mock_client.describe_db_instances.side_effect = self.service.client.exceptions.DBInstanceNotFoundFault()
        
        result = self.service.aws_db_instance(resource)
        
        self.assertIsNone(result)

    def test_aws_db_instance_missing_identifier(self):
        """Test aws_db_instance with missing identifier"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_db_instance(resource)
        
        self.assertIsNone(result)

    def test_aws_db_instance_empty_response(self):
        """Test aws_db_instance with empty response"""
        resource = {
            "change": {
                "after": {
                    "identifier": "test-db"
                }
            }
        }
        self.mock_client.describe_db_instances.return_value = {
            "DBInstances": []
        }
        
        result = self.service.aws_db_instance(resource)
        
        self.assertIsNone(result)

    def test_aws_db_instance_client_error(self):
        """Test aws_db_instance with ClientError"""
        resource = {
            "change": {
                "after": {
                    "identifier": "test-db"
                }
            }
        }
        self.mock_client.describe_db_instances.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "InvalidParameterValue"}}, "DescribeDBInstances"
        )
        
        result = self.service.aws_db_instance(resource)
        
        self.assertIsNone(result)

    def test_aws_db_subnet_group_success(self):
        """Test aws_db_subnet_group with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-subnet-group"
                }
            }
        }
        self.mock_client.describe_db_subnet_groups.return_value = {
            "DBSubnetGroups": [{"DBSubnetGroupName": "test-subnet-group"}]
        }
        
        result = self.service.aws_db_subnet_group(resource)
        
        self.assertEqual(result, "test-subnet-group")
        self.mock_client.describe_db_subnet_groups.assert_called_once_with(DBSubnetGroupName="test-subnet-group")

    def test_aws_db_subnet_group_not_found(self):
        """Test aws_db_subnet_group when subnet group doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-subnet-group"
                }
            }
        }
        self.mock_client.describe_db_subnet_groups.side_effect = self.service.client.exceptions.DBSubnetGroupNotFoundFault()
        
        result = self.service.aws_db_subnet_group(resource)
        
        self.assertIsNone(result)

    def test_aws_db_subnet_group_missing_name(self):
        """Test aws_db_subnet_group with missing name"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_db_subnet_group(resource)
        
        self.assertIsNone(result)

    def test_aws_db_subnet_group_empty_response(self):
        """Test aws_db_subnet_group with empty response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-subnet-group"
                }
            }
        }
        self.mock_client.describe_db_subnet_groups.return_value = {
            "DBSubnetGroups": []
        }
        
        result = self.service.aws_db_subnet_group(resource)
        
        self.assertIsNone(result)

    def test_aws_db_subnet_group_client_error(self):
        """Test aws_db_subnet_group with ClientError"""
        resource = {
            "change": {
                "after": {
                    "name": "test-subnet-group"
                }
            }
        }
        self.mock_client.describe_db_subnet_groups.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "InvalidParameterValue"}}, "DescribeDBSubnetGroups"
        )
        
        result = self.service.aws_db_subnet_group(resource)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
