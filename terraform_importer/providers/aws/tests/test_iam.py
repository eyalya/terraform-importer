import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
from terraform_importer.providers.aws.aws_services.iam import IAMService


class TestIAMService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_client = MagicMock()
        self.mock_sts_client = MagicMock()
        self.mock_session.client.side_effect = lambda service: {
            "iam": self.mock_client,
            "sts": self.mock_sts_client
        }.get(service, MagicMock())
        self.service = IAMService(self.mock_session)
        # Mock the exceptions attribute
        self.service.client.exceptions = MagicMock()
        self.service.client.exceptions.NoSuchEntityException = type(
            'NoSuchEntityException', (Exception,), {}
        )
        # Mock STS get_caller_identity
        self.mock_sts_client.get_caller_identity.return_value = {"Account": "123456789012"}

    def test_init(self):
        """Test IAMService initialization"""
        self.assertEqual(self.service.session, self.mock_session)

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = [
            "aws_iam_role",
            "aws_iam_policy",
            "aws_iam_role_policy",
            "aws_iam_role_policy_attachment",
            "aws_iam_user",
            "aws_iam_group",
            "aws_iam_instance_profile"
        ]
        self.assertEqual(resources, expected_resources)

    def test_aws_iam_role_success(self):
        """Test aws_iam_role with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-role"
                }
            }
        }
        self.mock_client.get_role.return_value = {
            "Role": {"RoleName": "test-role"}
        }
        
        result = self.service.aws_iam_role(resource)
        
        self.assertEqual(result, "test-role")
        self.mock_client.get_role.assert_called_once_with(RoleName="test-role")

    def test_aws_iam_role_not_found(self):
        """Test aws_iam_role when role doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-role"
                }
            }
        }
        self.mock_client.get_role.side_effect = self.service.client.exceptions.NoSuchEntityException()
        
        result = self.service.aws_iam_role(resource)
        
        self.assertIsNone(result)

    def test_aws_iam_role_missing_name(self):
        """Test aws_iam_role with missing name"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_iam_role(resource)
        
        self.assertIsNone(result)

    def test_aws_iam_policy_success(self):
        """Test aws_iam_policy with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-policy"
                }
            }
        }
        policy_arn = "arn:aws:iam::123456789012:policy/test-policy"
        self.mock_client.get_policy.return_value = {
            "Policy": {"PolicyName": "test-policy", "Arn": policy_arn}
        }
        
        result = self.service.aws_iam_policy(resource)
        
        self.assertEqual(result, policy_arn)

    def test_aws_iam_policy_not_found(self):
        """Test aws_iam_policy when policy doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-policy"
                }
            }
        }
        self.mock_client.get_policy.side_effect = self.service.client.exceptions.NoSuchEntityException()
        
        result = self.service.aws_iam_policy(resource)
        
        self.assertIsNone(result)

    def test_aws_iam_policy_with_path(self):
        """Test aws_iam_policy with path in ARN"""
        resource = {
            "change": {
                "after": {
                    "name": "langfuse-s3-access-dev",
                    "path": "/sa/"
                }
            }
        }
        policy_arn = "arn:aws:iam::123456789012:policy/sa/langfuse-s3-access-dev"
        self.mock_client.get_policy.return_value = {
            "Policy": {"PolicyName": "langfuse-s3-access-dev", "Arn": policy_arn}
        }
        
        result = self.service.aws_iam_policy(resource)
        
        self.assertEqual(result, policy_arn)
        self.mock_client.get_policy.assert_called_once_with(PolicyArn=policy_arn)

    def test_aws_iam_policy_with_path_no_leading_slash(self):
        """Test aws_iam_policy with path that doesn't start with /"""
        resource = {
            "change": {
                "after": {
                    "name": "test-policy",
                    "path": "sa/"
                }
            }
        }
        policy_arn = "arn:aws:iam::123456789012:policy/sa/test-policy"
        self.mock_client.get_policy.return_value = {
            "Policy": {"PolicyName": "test-policy", "Arn": policy_arn}
        }
        
        result = self.service.aws_iam_policy(resource)
        
        self.assertEqual(result, policy_arn)

    def test_aws_iam_policy_with_path_no_trailing_slash(self):
        """Test aws_iam_policy with path that doesn't end with /"""
        resource = {
            "change": {
                "after": {
                    "name": "test-policy",
                    "path": "/sa"
                }
            }
        }
        policy_arn = "arn:aws:iam::123456789012:policy/sa/test-policy"
        self.mock_client.get_policy.return_value = {
            "Policy": {"PolicyName": "test-policy", "Arn": policy_arn}
        }
        
        result = self.service.aws_iam_policy(resource)
        
        self.assertEqual(result, policy_arn)

    def test_aws_iam_role_policy_success(self):
        """Test aws_iam_role_policy with successful response"""
        resource = {
            "change": {
                "after": {
                    "role": "test-role",
                    "name": "test-policy"
                }
            }
        }
        self.mock_client.get_role_policy.return_value = {
            "PolicyName": "test-policy",
            "RoleName": "test-role"
        }
        
        result = self.service.aws_iam_role_policy(resource)
        
        self.assertEqual(result, "test-role:test-policy")

    def test_aws_iam_role_policy_not_found(self):
        """Test aws_iam_role_policy when policy doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "role": "test-role",
                    "name": "test-policy"
                }
            }
        }
        self.mock_client.get_role_policy.side_effect = self.service.client.exceptions.NoSuchEntityException()
        
        result = self.service.aws_iam_role_policy(resource)
        
        self.assertIsNone(result)

    def test_aws_iam_role_policy_attachment_success(self):
        """Test aws_iam_role_policy_attachment with successful response"""
        resource = {
            "change": {
                "after": {
                    "role": "test-role",
                    "policy_arn": "arn:aws:iam::aws:policy/ReadOnlyAccess"
                }
            }
        }
        self.mock_client.list_attached_role_policies.return_value = {
            "AttachedPolicies": [
                {"PolicyArn": "arn:aws:iam::aws:policy/ReadOnlyAccess"}
            ]
        }
        
        result = self.service.aws_iam_role_policy_attachment(resource)
        
        self.assertEqual(result, "test-role/arn:aws:iam::aws:policy/ReadOnlyAccess")

    def test_aws_iam_role_policy_attachment_not_found(self):
        """Test aws_iam_role_policy_attachment when attachment doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "role": "test-role",
                    "policy_arn": "arn:aws:iam::aws:policy/ReadOnlyAccess"
                }
            }
        }
        self.mock_client.list_attached_role_policies.return_value = {
            "AttachedPolicies": []
        }
        
        result = self.service.aws_iam_role_policy_attachment(resource)
        
        self.assertIsNone(result)

    def test_aws_iam_user_success(self):
        """Test aws_iam_user with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-user"
                }
            }
        }
        self.mock_client.get_user.return_value = {
            "User": {"UserName": "test-user"}
        }
        
        result = self.service.aws_iam_user(resource)
        
        self.assertEqual(result, "test-user")

    def test_aws_iam_user_not_found(self):
        """Test aws_iam_user when user doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-user"
                }
            }
        }
        self.mock_client.get_user.side_effect = self.service.client.exceptions.NoSuchEntityException()
        
        result = self.service.aws_iam_user(resource)
        
        self.assertIsNone(result)

    def test_aws_iam_group_success(self):
        """Test aws_iam_group with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-group"
                }
            }
        }
        self.mock_client.get_group.return_value = {
            "Group": {"GroupName": "test-group"}
        }
        
        result = self.service.aws_iam_group(resource)
        
        self.assertEqual(result, "test-group")

    def test_aws_iam_group_not_found(self):
        """Test aws_iam_group when group doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-group"
                }
            }
        }
        self.mock_client.get_group.side_effect = self.service.client.exceptions.NoSuchEntityException()
        
        result = self.service.aws_iam_group(resource)
        
        self.assertIsNone(result)

    def test_aws_iam_instance_profile_success(self):
        """Test aws_iam_instance_profile with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-profile"
                }
            }
        }
        self.mock_client.get_instance_profile.return_value = {
            "InstanceProfile": {"InstanceProfileName": "test-profile"}
        }
        
        result = self.service.aws_iam_instance_profile(resource)
        
        self.assertEqual(result, "test-profile")

    def test_aws_iam_instance_profile_not_found(self):
        """Test aws_iam_instance_profile when profile doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-profile"
                }
            }
        }
        self.mock_client.get_instance_profile.side_effect = self.service.client.exceptions.NoSuchEntityException()
        
        result = self.service.aws_iam_instance_profile(resource)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
