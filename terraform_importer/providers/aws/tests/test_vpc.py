import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
from terraform_importer.providers.aws.aws_services.vpc import VPCService


class TestVPCService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_client = MagicMock()
        self.mock_session.client.return_value = self.mock_client
        self.service = VPCService(self.mock_session)

    def test_init(self):
        """Test VPCService initialization"""
        self.assertEqual(self.service.session, self.mock_session)
        self.mock_session.client.assert_called_with("ec2")

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = [
            "aws_subnet",
            "aws_route_table",
            "aws_route_table_association"
        ]
        self.assertEqual(resources, expected_resources)

    def test_aws_route_table_success(self):
        """Test aws_route_table with successful response"""
        resource = {
            "change": {
                "after": {
                    "tags": {
                        "Name": "test-rt"
                    }
                }
            }
        }
        self.mock_client.describe_route_tables.return_value = {
            "RouteTables": [{"RouteTableId": "rtb-12345678"}]
        }
        
        result = self.service.aws_route_table(resource)
        
        self.assertEqual(result, "rtb-12345678")
        self.mock_client.describe_route_tables.assert_called_once()

    def test_aws_route_table_not_found(self):
        """Test aws_route_table when route table doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "tags": {
                        "Name": "test-rt"
                    }
                }
            }
        }
        self.mock_client.describe_route_tables.return_value = {
            "RouteTables": []
        }
        
        result = self.service.aws_route_table(resource)
        
        self.assertIsNone(result)

    def test_aws_route_table_missing_name_tag(self):
        """Test aws_route_table with missing Name tag"""
        resource = {
            "change": {
                "after": {
                    "tags": {}
                }
            }
        }
        
        result = self.service.aws_route_table(resource)
        
        self.assertIsNone(result)

    def test_aws_route_table_association_success(self):
        """Test aws_route_table_association with successful response"""
        resource = {
            "change": {
                "after": {
                    "route_table_id": "rtb-12345678",
                    "subnet_id": "subnet-12345678"
                }
            }
        }
        self.mock_client.describe_route_tables.return_value = {
            "RouteTables": [{
                "RouteTableId": "rtb-12345678",
                "Associations": [{
                    "SubnetId": "subnet-12345678",
                    "RouteTableAssociationId": "rtbassoc-12345678"
                }]
            }]
        }
        
        result = self.service.aws_route_table_association(resource)
        
        self.assertEqual(result, "subnet-12345678/rtb-12345678")

    def test_aws_route_table_association_not_found(self):
        """Test aws_route_table_association when association doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "route_table_id": "rtb-12345678",
                    "subnet_id": "subnet-12345678"
                }
            }
        }
        self.mock_client.describe_route_tables.return_value = {
            "RouteTables": [{
                "RouteTableId": "rtb-12345678",
                "Associations": []
            }]
        }
        
        result = self.service.aws_route_table_association(resource)
        
        self.assertIsNone(result)

    def test_aws_route_table_association_missing_fields(self):
        """Test aws_route_table_association with missing fields"""
        resource = {
            "change": {
                "after": {
                    "route_table_id": "rtb-12345678"
                }
            }
        }
        
        result = self.service.aws_route_table_association(resource)
        
        self.assertIsNone(result)

    def test_aws_route_table_exception_handling(self):
        """Test aws_route_table exception handling"""
        resource = {
            "change": {
                "after": {
                    "tags": {
                        "Name": "test-rt"
                    }
                }
            }
        }
        self.mock_client.describe_route_tables.side_effect = Exception("Test error")
        
        result = self.service.aws_route_table(resource)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
