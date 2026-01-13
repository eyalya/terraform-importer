import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
from terraform_importer.providers.aws.aws_services.s3 import S3Service


class TestS3Service(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_client = MagicMock()
        self.mock_session.client.return_value = self.mock_client
        self.service = S3Service(self.mock_session)

    def test_init(self):
        """Test S3Service initialization"""
        self.assertEqual(self.service.session, self.mock_session)
        self.mock_session.client.assert_called_with("s3")

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = [
            "aws_s3_bucket",
            "aws_s3_bucket_notification",
            "aws_s3_bucket_ownership_controls",
            "aws_s3_bucket_policy",
            "aws_s3_bucket_public_access_block",
            "aws_s3_bucket_server_side_encryption_configuration",
            "aws_s3_bucket_lifecycle_configuration",
            "aws_s3_bucket_versioning",
            "aws_s3_bucket_acl"
        ]
        self.assertEqual(resources, expected_resources)

    def test_aws_s3_bucket_success(self):
        """Test aws_s3_bucket with successful response"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        
        result = self.service.aws_s3_bucket(resource)
        
        self.assertEqual(result, "test-bucket")
        self.mock_client.head_bucket.assert_called_once_with(Bucket="test-bucket")

    def test_aws_s3_bucket_not_found(self):
        """Test aws_s3_bucket when bucket doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "404"}}, "HeadBucket"
        )
        
        result = self.service.aws_s3_bucket(resource)
        
        self.assertIsNone(result)

    def test_aws_s3_bucket_missing_name(self):
        """Test aws_s3_bucket with missing bucket name"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_s3_bucket(resource)
        
        self.assertIsNone(result)

    def test_aws_s3_bucket_notification_success(self):
        """Test aws_s3_bucket_notification with successful response"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        self.mock_client.get_bucket_notification_configuration.return_value = {
            "TopicConfigurations": [{"TopicArn": "arn:aws:sns:us-east-1:123456789012:test"}]
        }
        
        result = self.service.aws_s3_bucket_notification(resource)
        
        self.assertEqual(result, "test-bucket")

    def test_aws_s3_bucket_notification_no_config(self):
        """Test aws_s3_bucket_notification with no notification config"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        self.mock_client.get_bucket_notification_configuration.return_value = {}
        
        result = self.service.aws_s3_bucket_notification(resource)
        
        self.assertIsNone(result)

    def test_aws_s3_bucket_ownership_controls_success(self):
        """Test aws_s3_bucket_ownership_controls with successful response"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        self.mock_client.get_bucket_ownership_controls.return_value = {}
        
        result = self.service.aws_s3_bucket_ownership_controls(resource)
        
        self.assertEqual(result, "test-bucket")

    def test_aws_s3_bucket_policy_success(self):
        """Test aws_s3_bucket_policy with successful response"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        self.mock_client.get_bucket_policy.return_value = {"Policy": "{}"}
        
        result = self.service.aws_s3_bucket_policy(resource)
        
        self.assertEqual(result, "test-bucket")

    def test_aws_s3_bucket_public_access_block_success(self):
        """Test aws_s3_bucket_public_access_block with successful response"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        self.mock_client.get_public_access_block.return_value = {}
        
        result = self.service.aws_s3_bucket_public_access_block(resource)
        
        self.assertEqual(result, "test-bucket")

    def test_aws_s3_bucket_server_side_encryption_configuration_success(self):
        """Test aws_s3_bucket_server_side_encryption_configuration with successful response"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        self.mock_client.get_bucket_encryption.return_value = {}
        
        result = self.service.aws_s3_bucket_server_side_encryption_configuration(resource)
        
        self.assertEqual(result, "test-bucket")

    def test_aws_s3_bucket_lifecycle_configuration_success(self):
        """Test aws_s3_bucket_lifecycle_configuration with successful response"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        self.mock_client.get_bucket_lifecycle_configuration.return_value = {
            "Rules": [{"Id": "test-rule"}]
        }
        
        result = self.service.aws_s3_bucket_lifecycle_configuration(resource)
        
        self.assertEqual(result, "test-bucket")

    def test_aws_s3_bucket_lifecycle_configuration_no_rules(self):
        """Test aws_s3_bucket_lifecycle_configuration with no rules"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        self.mock_client.get_bucket_lifecycle_configuration.return_value = {}
        
        result = self.service.aws_s3_bucket_lifecycle_configuration(resource)
        
        self.assertIsNone(result)

    def test_aws_s3_bucket_versioning_success(self):
        """Test aws_s3_bucket_versioning with successful response"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        self.mock_client.get_bucket_versioning.return_value = {"Status": "Enabled"}
        
        result = self.service.aws_s3_bucket_versioning(resource)
        
        self.assertEqual(result, "test-bucket")

    def test_aws_s3_bucket_versioning_suspended(self):
        """Test aws_s3_bucket_versioning with suspended status"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        self.mock_client.get_bucket_versioning.return_value = {"Status": "Suspended"}
        
        result = self.service.aws_s3_bucket_versioning(resource)
        
        self.assertEqual(result, "test-bucket")

    def test_aws_s3_bucket_acl_success(self):
        """Test aws_s3_bucket_acl with successful response"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket",
                    "acl": "private",
                    "expected_bucket_owner": "123456789012"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        self.mock_client.get_bucket_acl.return_value = {}
        
        result = self.service.aws_s3_bucket_acl(resource)
        
        self.assertEqual(result, "test-bucket,123456789012,private")

    def test_aws_s3_bucket_acl_no_optional_fields(self):
        """Test aws_s3_bucket_acl without optional fields"""
        resource = {
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }
        self.mock_client.head_bucket.return_value = {}
        self.mock_client.get_bucket_acl.return_value = {}
        
        result = self.service.aws_s3_bucket_acl(resource)
        
        self.assertEqual(result, "test-bucket")


if __name__ == "__main__":
    unittest.main()
