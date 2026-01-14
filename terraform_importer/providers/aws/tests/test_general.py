import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
from terraform_importer.providers.aws.aws_services.general import GENERALService


class TestGENERALService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_sqs_client = MagicMock()
        self.mock_sns_client = MagicMock()
        self.mock_acm_client = MagicMock()
        self.mock_cloudfront_client = MagicMock()
        self.mock_codebuild_client = MagicMock()
        self.mock_route53_client = MagicMock()
        self.mock_elasticbeanstalk_client = MagicMock()
        self.mock_elasticache_client = MagicMock()
        
        def client_side_effect(service):
            clients = {
                "sqs": self.mock_sqs_client,
                "sns": self.mock_sns_client,
                "acm": self.mock_acm_client,
                "cloudfront": self.mock_cloudfront_client,
                "codebuild": self.mock_codebuild_client,
                "route53": self.mock_route53_client,
                "elasticbeanstalk": self.mock_elasticbeanstalk_client,
                "elasticache": self.mock_elasticache_client
            }
            return clients.get(service, MagicMock())
        
        self.mock_session.client.side_effect = client_side_effect
        self.service = GENERALService(self.mock_session)
        # Add missing clients that are used but not initialized
        self.service.route53_client = self.mock_route53_client
        self.service.elasticbeanstalk_client = self.mock_elasticbeanstalk_client
        self.service.elasticache_client = self.mock_elasticache_client
        
        # Mock exceptions
        self.service.sqs_client.exceptions = MagicMock()
        self.service.sqs_client.exceptions.QueueDoesNotExist = type(
            'QueueDoesNotExist', (Exception,), {}
        )

    def test_init(self):
        """Test GENERALService initialization"""
        self.assertEqual(self.service.session, self.mock_session)

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = [
            "aws_sqs_queue",
            "aws_sns_topic",
            "aws_route53_record",
            "aws_acm_certificate",
            "aws_elastic_beanstalk_application",
            "aws_elasticache_cluster",
            "aws_elasticache_subnet_group",
            "aws_codebuild_project",
            "aws_cloudfront_distribution",
            "aws_codebuild_source_credential"
        ]
        self.assertEqual(resources, expected_resources)

    def test_aws_sqs_queue_success(self):
        """Test aws_sqs_queue with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-queue"
                }
            }
        }
        self.mock_sqs_client.get_queue_url.return_value = {
            "QueueUrl": "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"
        }
        
        result = self.service.aws_sqs_queue(resource)
        
        self.assertEqual(result, "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue")

    def test_aws_sqs_queue_not_found(self):
        """Test aws_sqs_queue when queue doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-queue"
                }
            }
        }
        self.mock_sqs_client.get_queue_url.side_effect = self.service.sqs_client.exceptions.QueueDoesNotExist()
        
        result = self.service.aws_sqs_queue(resource)
        
        self.assertIsNone(result)

    def test_aws_sns_topic_success(self):
        """Test aws_sns_topic with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-topic"
                }
            }
        }
        mock_paginator = MagicMock()
        self.mock_sns_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{
            "Topics": [{
                "TopicArn": "arn:aws:sns:us-east-1:123456789012:test-topic"
            }]
        }]
        
        result = self.service.aws_sns_topic(resource)
        
        self.assertEqual(result, "arn:aws:sns:us-east-1:123456789012:test-topic")

    def test_aws_sns_topic_not_found(self):
        """Test aws_sns_topic when topic doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-topic"
                }
            }
        }
        mock_paginator = MagicMock()
        self.mock_sns_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{
            "Topics": []
        }]
        
        result = self.service.aws_sns_topic(resource)
        
        self.assertIsNone(result)

    def test_aws_route53_record_success(self):
        """Test aws_route53_record with successful response"""
        resource = {
            "change": {
                "after": {
                    "zone_id": "Z1234567890",
                    "name": "test.example.com",
                    "type": "A"
                }
            }
        }
        mock_paginator = MagicMock()
        self.mock_route53_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{
            "ResourceRecordSets": [{
                "Name": "test.example.com",
                "Type": "A"
            }]
        }]
        
        result = self.service.aws_route53_record(resource)
        
        self.assertEqual(result, "Z1234567890_test.example.com_A")

    def test_aws_route53_record_not_found(self):
        """Test aws_route53_record when record doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "zone_id": "Z1234567890",
                    "name": "test.example.com",
                    "type": "A"
                }
            }
        }
        mock_paginator = MagicMock()
        self.mock_route53_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{
            "ResourceRecordSets": []
        }]
        
        result = self.service.aws_route53_record(resource)
        
        self.assertIsNone(result)

    def test_aws_acm_certificate_success(self):
        """Test aws_acm_certificate with successful response"""
        resource = {
            "change": {
                "after": {
                    "domain_name": "example.com"
                }
            }
        }
        mock_paginator = MagicMock()
        self.mock_acm_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{
            "CertificateSummaryList": [{
                "DomainName": "example.com",
                "CertificateArn": "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012"
            }]
        }]
        
        result = self.service.aws_acm_certificate(resource)
        
        self.assertEqual(result, "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012")

    def test_aws_acm_certificate_not_found(self):
        """Test aws_acm_certificate when certificate doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "domain_name": "example.com"
                }
            }
        }
        mock_paginator = MagicMock()
        self.mock_acm_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{
            "CertificateSummaryList": []
        }]
        
        result = self.service.aws_acm_certificate(resource)
        
        self.assertIsNone(result)

    def test_aws_elastic_beanstalk_application_success(self):
        """Test aws_elastic_beanstalk_application with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-app"
                }
            }
        }
        self.mock_elasticbeanstalk_client.describe_applications.return_value = {
            "Applications": [{"ApplicationName": "test-app"}]
        }
        
        result = self.service.aws_elastic_beanstalk_application(resource)
        
        self.assertEqual(result, "test-app")

    def test_aws_elasticache_cluster_success(self):
        """Test aws_elasticache_cluster with successful response"""
        resource = {
            "change": {
                "after": {
                    "cluster_id": "test-cluster"
                }
            }
        }
        self.mock_elasticache_client.describe_cache_clusters.return_value = {
            "CacheClusters": [{"CacheClusterId": "test-cluster"}]
        }
        
        result = self.service.aws_elasticache_cluster(resource)
        
        self.assertEqual(result, "test-cluster")

    def test_aws_elasticache_subnet_group_success(self):
        """Test aws_elasticache_subnet_group with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-subnet-group"
                }
            }
        }
        self.mock_elasticache_client.describe_cache_subnet_groups.return_value = {
            "CacheSubnetGroups": [{"CacheSubnetGroupName": "test-subnet-group"}]
        }
        
        result = self.service.aws_elasticache_subnet_group(resource)
        
        self.assertEqual(result, "test-subnet-group")

    def test_aws_codebuild_project_success(self):
        """Test aws_codebuild_project with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-project"
                }
            }
        }
        self.mock_codebuild_client.batch_get_projects.return_value = {
            "projects": [{"name": "test-project"}]
        }
        
        result = self.service.aws_codebuild_project(resource)
        
        self.assertEqual(result, "test-project")

    def test_aws_cloudfront_distribution_success(self):
        """Test aws_cloudfront_distribution with successful response"""
        resource = {
            "change": {
                "after": {
                    "aliases": ["example.com"]
                }
            }
        }
        mock_paginator = MagicMock()
        self.mock_cloudfront_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{
            "DistributionList": {
                "Items": [{
                    "Id": "E1234567890",
                    "Aliases": {
                        "Items": ["example.com"]
                    }
                }]
            }
        }]
        
        result = self.service.aws_cloudfront_distribution(resource)
        
        self.assertEqual(result, "E1234567890")

    def test_aws_codebuild_source_credential_success(self):
        """Test aws_codebuild_source_credential with successful response"""
        resource = {
            "change": {
                "after": {
                    "auth_type": "BASIC_AUTH",
                    "server_type": "GITHUB"
                }
            }
        }
        self.mock_codebuild_client.list_source_credentials.return_value = {
            "sourceCredentialsInfos": [{
                "authType": "BASIC_AUTH",
                "serverType": "GITHUB",
                "arn": "arn:aws:codebuild:us-east-1:123456789012:token/github"
            }]
        }
        
        result = self.service.aws_codebuild_source_credential(resource)
        
        self.assertEqual(result, "arn:aws:codebuild:us-east-1:123456789012:token/github")


if __name__ == "__main__":
    unittest.main()
