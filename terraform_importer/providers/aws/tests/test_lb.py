import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
from terraform_importer.providers.aws.aws_services.lb import LoadBalancerService


class TestLoadBalancerService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_client = MagicMock()
        self.mock_session.client.return_value = self.mock_client
        self.service = LoadBalancerService(self.mock_session)

    def test_init(self):
        """Test LoadBalancerService initialization"""
        self.assertEqual(self.service.session, self.mock_session)
        self.mock_session.client.assert_called_with("elbv2")

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = [
            "aws_lb_target_group",
            "aws_lb_listener"
        ]
        self.assertEqual(resources, expected_resources)

    def test_aws_lb_target_group_success(self):
        """Test aws_lb_target_group with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-tg"
                }
            }
        }
        mock_paginator = MagicMock()
        self.mock_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{
            "TargetGroups": [{
                "TargetGroupName": "test-tg",
                "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890123456"
            }]
        }]
        
        result = self.service.aws_lb_target_group(resource)
        
        self.assertEqual(result, "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890123456")

    def test_aws_lb_target_group_not_found(self):
        """Test aws_lb_target_group when target group doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-tg"
                }
            }
        }
        mock_paginator = MagicMock()
        self.mock_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{
            "TargetGroups": []
        }]
        
        result = self.service.aws_lb_target_group(resource)
        
        self.assertIsNone(result)

    def test_aws_lb_target_group_missing_name(self):
        """Test aws_lb_target_group with missing name"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_lb_target_group(resource)
        
        self.assertIsNone(result)

    def test_aws_lb_target_group_client_error(self):
        """Test aws_lb_target_group with ClientError"""
        resource = {
            "change": {
                "after": {
                    "name": "test-tg"
                }
            }
        }
        mock_paginator = MagicMock()
        self.mock_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "TargetGroupNotFound"}}, "DescribeTargetGroups"
        )
        
        result = self.service.aws_lb_target_group(resource)
        
        self.assertIsNone(result)

    def test_aws_lb_listener_success(self):
        """Test aws_lb_listener with successful response"""
        resource = {
            "change": {
                "after": {
                    "load_balancer_arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/test-lb/1234567890123456",
                    "port": 80,
                    "protocol": "HTTP"
                }
            }
        }
        self.mock_client.describe_listeners.return_value = {
            "Listeners": [{
                "ListenerArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/test-lb/1234567890123456/1234567890123456",
                "Port": 80,
                "Protocol": "HTTP"
            }]
        }
        
        result = self.service.aws_lb_listener(resource)
        
        self.assertIsNotNone(result)
        self.assertEqual(result, "arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/test-lb/1234567890123456/1234567890123456")

    def test_aws_lb_listener_not_found(self):
        """Test aws_lb_listener when listener doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "load_balancer_arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/test-lb/1234567890123456",
                    "port": 80,
                    "protocol": "HTTP"
                }
            }
        }
        self.mock_client.describe_listeners.return_value = {
            "Listeners": []
        }
        
        result = self.service.aws_lb_listener(resource)
        
        self.assertIsNone(result)

    def test_aws_lb_listener_missing_fields(self):
        """Test aws_lb_listener with missing fields"""
        resource = {
            "change": {
                "after": {
                    "load_balancer_arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/test-lb/1234567890123456"
                }
            }
        }
        
        result = self.service.aws_lb_listener(resource)
        
        self.assertIsNone(result)

    def test_aws_lb_listener_client_error(self):
        """Test aws_lb_listener with ClientError"""
        resource = {
            "change": {
                "after": {
                    "load_balancer_arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/test-lb/1234567890123456",
                    "port": 80,
                    "protocol": "HTTP"
                }
            }
        }
        self.mock_client.describe_listeners.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "LoadBalancerNotFound"}}, "DescribeListeners"
        )
        
        result = self.service.aws_lb_listener(resource)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
