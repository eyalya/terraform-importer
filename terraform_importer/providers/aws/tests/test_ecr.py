import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
from terraform_importer.providers.aws.aws_services.ecr import ECRService


class TestECRService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_client = MagicMock()
        self.mock_session.client.return_value = self.mock_client
        self.service = ECRService(self.mock_session)
        # Mock the exceptions attribute
        self.service.client.exceptions = MagicMock()
        self.service.client.exceptions.RepositoryNotFoundException = type(
            'RepositoryNotFoundException', (Exception,), {}
        )
        self.service.client.exceptions.LifecyclePolicyNotFoundException = type(
            'LifecyclePolicyNotFoundException', (Exception,), {}
        )

    def test_init(self):
        """Test ECRService initialization"""
        self.assertEqual(self.service.session, self.mock_session)
        self.mock_session.client.assert_called_with("ecr")

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = [
            "aws_ecr_repository",
            "aws_ecr_lifecycle_policy",
            "aws_ecr_registry_scanning_configuration"
        ]
        self.assertEqual(resources, expected_resources)

    def test_aws_ecr_repository_success(self):
        """Test aws_ecr_repository with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-repo"
                }
            }
        }
        self.mock_client.describe_repositories.return_value = {
            "repositories": [{"repositoryName": "test-repo"}]
        }
        
        result = self.service.aws_ecr_repository(resource)
        
        self.assertEqual(result, "test-repo")
        self.mock_client.describe_repositories.assert_called_once_with(
            repositoryNames=["test-repo"]
        )

    def test_aws_ecr_repository_not_found(self):
        """Test aws_ecr_repository when repository doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-repo"
                }
            }
        }
        self.mock_client.describe_repositories.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "RepositoryNotFoundException"}}, "DescribeRepositories"
        )
        
        result = self.service.aws_ecr_repository(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_repository_not_found_exception(self):
        """Test aws_ecr_repository when repository doesn't exist using exception"""
        resource = {
            "change": {
                "after": {
                    "name": "test-repo"
                }
            }
        }
        self.mock_client.describe_repositories.side_effect = self.service.client.exceptions.RepositoryNotFoundException()
        
        result = self.service.aws_ecr_repository(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_repository_missing_name(self):
        """Test aws_ecr_repository when name is missing"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_ecr_repository(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_repository_empty_response(self):
        """Test aws_ecr_repository when response is empty"""
        resource = {
            "change": {
                "after": {
                    "name": "test-repo"
                }
            }
        }
        self.mock_client.describe_repositories.return_value = {
            "repositories": []
        }
        
        result = self.service.aws_ecr_repository(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_repository_client_error(self):
        """Test aws_ecr_repository with other ClientError"""
        resource = {
            "change": {
                "after": {
                    "name": "test-repo"
                }
            }
        }
        self.mock_client.describe_repositories.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "AccessDeniedException"}}, "DescribeRepositories"
        )
        
        result = self.service.aws_ecr_repository(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_repository_key_error(self):
        """Test aws_ecr_repository with KeyError"""
        resource = {
            "change": {}
        }
        
        result = self.service.aws_ecr_repository(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_repository_unexpected_error(self):
        """Test aws_ecr_repository with unexpected error"""
        resource = {
            "change": {
                "after": {
                    "name": "test-repo"
                }
            }
        }
        self.mock_client.describe_repositories.side_effect = Exception("Unexpected error")
        
        result = self.service.aws_ecr_repository(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_lifecycle_policy_success(self):
        """Test aws_ecr_lifecycle_policy with successful response"""
        resource = {
            "change": {
                "after": {
                    "repository": "test-repo"
                }
            }
        }
        self.mock_client.get_lifecycle_policy.return_value = {
            "repositoryName": "test-repo",
            "lifecyclePolicyText": "{\"rules\":[]}"
        }
        
        result = self.service.aws_ecr_lifecycle_policy(resource)
        
        self.assertEqual(result, "test-repo")
        self.mock_client.get_lifecycle_policy.assert_called_once_with(
            repositoryName="test-repo"
        )

    def test_aws_ecr_lifecycle_policy_not_found(self):
        """Test aws_ecr_lifecycle_policy when lifecycle policy doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "repository": "test-repo"
                }
            }
        }
        self.mock_client.get_lifecycle_policy.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "LifecyclePolicyNotFoundException"}}, "GetLifecyclePolicy"
        )
        
        result = self.service.aws_ecr_lifecycle_policy(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_lifecycle_policy_not_found_exception(self):
        """Test aws_ecr_lifecycle_policy when lifecycle policy doesn't exist using exception"""
        resource = {
            "change": {
                "after": {
                    "repository": "test-repo"
                }
            }
        }
        self.mock_client.get_lifecycle_policy.side_effect = self.service.client.exceptions.LifecyclePolicyNotFoundException()
        
        result = self.service.aws_ecr_lifecycle_policy(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_lifecycle_policy_repository_not_found(self):
        """Test aws_ecr_lifecycle_policy when repository doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "repository": "test-repo"
                }
            }
        }
        self.mock_client.get_lifecycle_policy.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "RepositoryNotFoundException"}}, "GetLifecyclePolicy"
        )
        
        result = self.service.aws_ecr_lifecycle_policy(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_lifecycle_policy_repository_not_found_exception(self):
        """Test aws_ecr_lifecycle_policy when repository doesn't exist using exception"""
        resource = {
            "change": {
                "after": {
                    "repository": "test-repo"
                }
            }
        }
        self.mock_client.get_lifecycle_policy.side_effect = self.service.client.exceptions.RepositoryNotFoundException()
        
        result = self.service.aws_ecr_lifecycle_policy(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_lifecycle_policy_missing_repository(self):
        """Test aws_ecr_lifecycle_policy when repository is missing"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_ecr_lifecycle_policy(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_lifecycle_policy_empty_response(self):
        """Test aws_ecr_lifecycle_policy when response is empty"""
        resource = {
            "change": {
                "after": {
                    "repository": "test-repo"
                }
            }
        }
        self.mock_client.get_lifecycle_policy.return_value = {}
        
        result = self.service.aws_ecr_lifecycle_policy(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_lifecycle_policy_client_error(self):
        """Test aws_ecr_lifecycle_policy with other ClientError"""
        resource = {
            "change": {
                "after": {
                    "repository": "test-repo"
                }
            }
        }
        self.mock_client.get_lifecycle_policy.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "AccessDeniedException"}}, "GetLifecyclePolicy"
        )
        
        result = self.service.aws_ecr_lifecycle_policy(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_lifecycle_policy_key_error(self):
        """Test aws_ecr_lifecycle_policy with KeyError"""
        resource = {
            "change": {}
        }
        
        result = self.service.aws_ecr_lifecycle_policy(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_lifecycle_policy_unexpected_error(self):
        """Test aws_ecr_lifecycle_policy with unexpected error"""
        resource = {
            "change": {
                "after": {
                    "repository": "test-repo"
                }
            }
        }
        self.mock_client.get_lifecycle_policy.side_effect = Exception("Unexpected error")
        
        result = self.service.aws_ecr_lifecycle_policy(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_registry_scanning_configuration_success(self):
        """Test aws_ecr_registry_scanning_configuration with successful response"""
        resource = {
            "change": {
                "after": {}
            }
        }
        self.mock_client.get_registry_scanning_configuration.return_value = {
            "registryId": "123456789012",
            "scanningConfiguration": {
                "scanType": "BASIC"
            }
        }
        
        result = self.service.aws_ecr_registry_scanning_configuration(resource)
        
        self.assertEqual(result, "default")
        self.mock_client.get_registry_scanning_configuration.assert_called_once()

    def test_aws_ecr_registry_scanning_configuration_access_denied(self):
        """Test aws_ecr_registry_scanning_configuration with AccessDeniedException"""
        resource = {
            "change": {
                "after": {}
            }
        }
        self.mock_client.get_registry_scanning_configuration.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "AccessDeniedException"}}, "GetRegistryScanningConfiguration"
        )
        
        result = self.service.aws_ecr_registry_scanning_configuration(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_registry_scanning_configuration_invalid_parameter(self):
        """Test aws_ecr_registry_scanning_configuration with InvalidParameterException"""
        resource = {
            "change": {
                "after": {}
            }
        }
        self.mock_client.get_registry_scanning_configuration.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "InvalidParameterException"}}, "GetRegistryScanningConfiguration"
        )
        
        result = self.service.aws_ecr_registry_scanning_configuration(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_registry_scanning_configuration_validation_exception(self):
        """Test aws_ecr_registry_scanning_configuration with ValidationException"""
        resource = {
            "change": {
                "after": {}
            }
        }
        self.mock_client.get_registry_scanning_configuration.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "ValidationException"}}, "GetRegistryScanningConfiguration"
        )
        
        result = self.service.aws_ecr_registry_scanning_configuration(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_registry_scanning_configuration_other_client_error(self):
        """Test aws_ecr_registry_scanning_configuration with other ClientError"""
        resource = {
            "change": {
                "after": {}
            }
        }
        self.mock_client.get_registry_scanning_configuration.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "ServiceException"}}, "GetRegistryScanningConfiguration"
        )
        
        result = self.service.aws_ecr_registry_scanning_configuration(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_registry_scanning_configuration_key_error(self):
        """Test aws_ecr_registry_scanning_configuration with KeyError"""
        resource = {
            "change": {}
        }
        
        result = self.service.aws_ecr_registry_scanning_configuration(resource)
        
        self.assertIsNone(result)

    def test_aws_ecr_registry_scanning_configuration_unexpected_error(self):
        """Test aws_ecr_registry_scanning_configuration with unexpected error"""
        resource = {
            "change": {
                "after": {}
            }
        }
        self.mock_client.get_registry_scanning_configuration.side_effect = Exception("Unexpected error")
        
        result = self.service.aws_ecr_registry_scanning_configuration(resource)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
