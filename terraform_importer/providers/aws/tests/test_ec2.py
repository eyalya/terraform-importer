import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
from terraform_importer.providers.aws.aws_services.ec2 import EC2Service


class TestEC2Service(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_client = MagicMock()
        self.mock_session.client.return_value = self.mock_client
        self.service = EC2Service(self.mock_session)

    def test_init(self):
        """Test EC2Service initialization"""
        self.assertEqual(self.service.session, self.mock_session)
        self.mock_session.client.assert_called_with("ec2")

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = [
            "aws_security_group",
            "aws_security_group_rule",
            "aws_autoscaling_group",
            "aws_key_pair"
        ]
        self.assertEqual(resources, expected_resources)

    def test_aws_security_group_success(self):
        """Test aws_security_group with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-sg"
                }
            }
        }
        self.mock_client.describe_security_groups.return_value = {
            "SecurityGroups": [{"GroupId": "sg-12345678"}]
        }
        
        result = self.service.aws_security_group(resource)
        
        self.assertEqual(result, "sg-12345678")
        self.mock_client.describe_security_groups.assert_called_once()

    def test_aws_security_group_not_found(self):
        """Test aws_security_group when security group doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-sg"
                }
            }
        }
        self.mock_client.describe_security_groups.return_value = {
            "SecurityGroups": []
        }
        
        result = self.service.aws_security_group(resource)
        
        self.assertIsNone(result)

    def test_aws_security_group_missing_name(self):
        """Test aws_security_group with missing name"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_security_group(resource)
        
        self.assertIsNone(result)

    def test_aws_security_group_rule_success(self):
        """Test aws_security_group_rule with successful response"""
        resource = {
            "change": {
                "after": {
                    "security_group_id": "sg-12345678",
                    "type": "ingress",
                    "protocol": "tcp",
                    "from_port": 80,
                    "to_port": 80,
                    "cidr_blocks": ["0.0.0.0/0"]
                }
            }
        }
        self.mock_client.describe_security_group_rules.return_value = {
            "SecurityGroupRules": [
                {
                    "GroupId": "sg-12345678",
                    "IsEgress": False,
                    "IpProtocol": "tcp",
                    "FromPort": 80,
                    "ToPort": 80
                }
            ]
        }
        
        result = self.service.aws_security_group_rule(resource)
        
        self.assertIsNotNone(result)

    def test_aws_security_group_rule_missing_security_group_id(self):
        """Test aws_security_group_rule with missing security_group_id"""
        resource = {
            "change": {
                "after": {
                    "type": "ingress",
                    "protocol": "tcp"
                }
            }
        }
        
        result = self.service.aws_security_group_rule(resource)
        
        self.assertIsNone(result)

    def test_aws_autoscaling_group_success(self):
        """Test aws_autoscaling_group with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-asg"
                }
            }
        }
        self.mock_client.describe_auto_scaling_groups.return_value = {
            "AutoScalingGroups": [{"AutoScalingGroupName": "test-asg"}]
        }
        
        result = self.service.aws_autoscaling_group(resource)
        
        self.assertEqual(result, "test-asg")

    def test_aws_autoscaling_group_not_found(self):
        """Test aws_autoscaling_group when ASG doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-asg"
                }
            }
        }
        self.mock_client.describe_auto_scaling_groups.return_value = {
            "AutoScalingGroups": []
        }
        
        result = self.service.aws_autoscaling_group(resource)
        
        self.assertIsNone(result)

    def test_aws_key_pair_success(self):
        """Test aws_key_pair with successful response"""
        resource = {
            "change": {
                "after": {
                    "key_name": "test-key"
                }
            }
        }
        self.mock_client.describe_key_pairs.return_value = {
            "KeyPairs": [{"KeyName": "test-key"}]
        }
        
        result = self.service.aws_key_pair(resource)
        
        self.assertEqual(result, "test-key")

    def test_aws_key_pair_not_found(self):
        """Test aws_key_pair when key pair doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "key_name": "test-key"
                }
            }
        }
        self.mock_client.describe_key_pairs.return_value = {
            "KeyPairs": []
        }
        
        result = self.service.aws_key_pair(resource)
        
        self.assertIsNone(result)

    def test_aws_key_pair_client_error(self):
        """Test aws_key_pair with ClientError"""
        resource = {
            "change": {
                "after": {
                    "key_name": "test-key"
                }
            }
        }
        self.mock_client.describe_key_pairs.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "InvalidKeyPair.NotFound"}}, "DescribeKeyPairs"
        )
        
        result = self.service.aws_key_pair(resource)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
