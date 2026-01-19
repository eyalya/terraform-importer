import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
from terraform_importer.providers.aws.aws_services.ecs import ECSService


class TestECSService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_client = MagicMock()
        self.mock_sd_client = MagicMock()
        self.mock_session.client.side_effect = lambda service: {
            "ecs": self.mock_client,
            "servicediscovery": self.mock_sd_client
        }.get(service, MagicMock())
        self.service = ECSService(self.mock_session)

    def test_init(self):
        """Test ECSService initialization"""
        self.assertEqual(self.service.session, self.mock_session)

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = [
            "aws_ecs_service",
            "aws_ecs_task_definition",
            "aws_ecs_cluster_capacity_providers",
            "aws_service_discovery_service"
        ]
        self.assertEqual(resources, expected_resources)

    def test_aws_ecs_service_success(self):
        """Test aws_ecs_service with successful response"""
        resource = {
            "change": {
                "after": {
                    "cluster": "test-cluster",
                    "name": "test-service"
                }
            }
        }
        self.mock_client.describe_services.return_value = {
            "services": [{
                "serviceName": "test-service",
                "status": "ACTIVE"
            }]
        }
        
        result = self.service.aws_ecs_service(resource)
        
        self.assertEqual(result, "test-cluster/test-service")
        self.mock_client.describe_services.assert_called_once_with(
            cluster="test-cluster",
            services=["test-service"]
        )

    def test_aws_ecs_service_inactive(self):
        """Test aws_ecs_service when service is INACTIVE"""
        resource = {
            "change": {
                "after": {
                    "cluster": "test-cluster",
                    "name": "test-service"
                }
            }
        }
        self.mock_client.describe_services.return_value = {
            "services": [{
                "serviceName": "test-service",
                "status": "INACTIVE"
            }]
        }
        
        result = self.service.aws_ecs_service(resource)
        
        self.assertIsNone(result)

    def test_aws_ecs_service_missing_cluster(self):
        """Test aws_ecs_service with missing cluster"""
        resource = {
            "change": {
                "after": {
                    "name": "test-service"
                }
            }
        }
        
        result = self.service.aws_ecs_service(resource)
        
        self.assertIsNone(result)

    def test_aws_ecs_task_definition_success(self):
        """Test aws_ecs_task_definition with successful response"""
        resource = {
            "change": {
                "after": {
                    "family": "test-family"
                }
            }
        }
        self.mock_client.describe_task_definition.return_value = {
            "taskDefinition": {
                "taskDefinitionArn": "arn:aws:ecs:us-east-1:123456789012:task-definition/test-family:1"
            }
        }
        
        result = self.service.aws_ecs_task_definition(resource)
        
        self.assertEqual(result, "arn:aws:ecs:us-east-1:123456789012:task-definition/test-family:1")

    def test_aws_ecs_task_definition_not_found(self):
        """Test aws_ecs_task_definition when task definition doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "family": "test-family"
                }
            }
        }
        self.mock_client.describe_task_definition.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "ClientException"}}, "DescribeTaskDefinition"
        )
        
        result = self.service.aws_ecs_task_definition(resource)
        
        self.assertIsNone(result)

    def test_aws_ecs_task_definition_missing_family(self):
        """Test aws_ecs_task_definition with missing family"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_ecs_task_definition(resource)
        
        self.assertIsNone(result)

    def test_aws_ecs_cluster_capacity_providers_success(self):
        """Test aws_ecs_cluster_capacity_providers with successful response"""
        resource = {
            "change": {
                "after": {
                    "cluster_name": "test-cluster"
                }
            }
        }
        self.mock_client.describe_clusters.return_value = {
            "clusters": [{"clusterName": "test-cluster"}]
        }
        
        result = self.service.aws_ecs_cluster_capacity_providers(resource)
        
        self.assertEqual(result, "test-cluster")

    def test_aws_ecs_cluster_capacity_providers_not_found(self):
        """Test aws_ecs_cluster_capacity_providers when cluster doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "cluster_name": "test-cluster"
                }
            }
        }
        self.mock_client.describe_clusters.return_value = {
            "clusters": []
        }
        
        result = self.service.aws_ecs_cluster_capacity_providers(resource)
        
        self.assertIsNone(result)

    def test_aws_ecs_cluster_capacity_providers_missing_name(self):
        """Test aws_ecs_cluster_capacity_providers with missing cluster_name"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_ecs_cluster_capacity_providers(resource)
        
        self.assertIsNone(result)

    def test_aws_service_discovery_service_success(self):
        """Test aws_service_discovery_service with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-service",
                    "dns_config": [{
                        "namespace_id": "ns-12345678"
                    }]
                }
            }
        }
        mock_paginator = MagicMock()
        self.mock_sd_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{
            "Services": [{
                "Id": "srv-12345678",
                "Name": "test-service"
            }]
        }]
        
        result = self.service.aws_service_discovery_service(resource)
        
        self.assertEqual(result, "srv-12345678")

    def test_aws_service_discovery_service_not_found(self):
        """Test aws_service_discovery_service when service doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-service",
                    "dns_config": [{
                        "namespace_id": "ns-12345678"
                    }]
                }
            }
        }
        mock_paginator = MagicMock()
        self.mock_sd_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{
            "Services": []
        }]
        
        result = self.service.aws_service_discovery_service(resource)
        
        self.assertIsNone(result)

    def test_aws_service_discovery_service_missing_fields(self):
        """Test aws_service_discovery_service with missing fields"""
        resource = {
            "change": {
                "after": {
                    "name": "test-service"
                }
            }
        }
        
        result = self.service.aws_service_discovery_service(resource)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
