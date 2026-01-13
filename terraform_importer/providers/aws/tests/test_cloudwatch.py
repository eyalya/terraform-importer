import unittest
from unittest.mock import Mock, MagicMock, patch
import boto3
import botocore.exceptions
from terraform_importer.providers.aws.aws_services.cloudwatch import CloudWatchService


class TestCloudWatchService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=boto3.Session)
        self.mock_session.region_name = "us-east-1"
        self.mock_logs_client = MagicMock()
        self.mock_events_client = MagicMock()
        self.mock_sts_client = MagicMock()
        
        def client_side_effect(service):
            clients = {
                "logs": self.mock_logs_client,
                "events": self.mock_events_client,
                "sts": self.mock_sts_client
            }
            return clients.get(service, MagicMock())
        
        self.mock_session.client.side_effect = client_side_effect
        self.mock_sts_client.get_caller_identity.return_value = {"Account": "123456789012"}
        self.service = CloudWatchService(self.mock_session)

    def test_init(self):
        """Test CloudWatchService initialization"""
        self.assertEqual(self.service.session, self.mock_session)
        self.assertEqual(self.service.account_id, "123456789012")
        self.assertEqual(self.service.region, "us-east-1")

    def test_get_resource_list(self):
        """Test get_resource_list returns correct resources"""
        resources = self.service.get_resource_list()
        expected_resources = [
            "aws_cloudwatch_query_definition",
            "aws_cloudwatch_event_target",
            "aws_cloudwatch_log_group",
            "aws_cloudwatch_metric_alarm",
            "aws_cloudwatch_event_rule",
            "aws_cloudwatch_log_metric_filter",
            "aws_cloudwatch_query_definition"
        ]
        self.assertEqual(resources, expected_resources)

    def test_aws_cloudwatch_event_target_success(self):
        """Test aws_cloudwatch_event_target with successful response"""
        resource = {
            "change": {
                "after": {
                    "rule": "test-rule",
                    "target_id": "test-target"
                }
            }
        }
        self.mock_events_client.list_targets_by_rule.return_value = {
            "Targets": [{"Id": "test-target"}]
        }
        
        result = self.service.aws_cloudwatch_event_target(resource)
        
        self.assertEqual(result, "test-rule/test-target")

    def test_aws_cloudwatch_event_target_not_found(self):
        """Test aws_cloudwatch_event_target when target doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "rule": "test-rule",
                    "target_id": "test-target"
                }
            }
        }
        self.mock_events_client.list_targets_by_rule.return_value = {
            "Targets": []
        }
        
        result = self.service.aws_cloudwatch_event_target(resource)
        
        self.assertIsNone(result)

    def test_aws_cloudwatch_log_group_success(self):
        """Test aws_cloudwatch_log_group with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "/aws/lambda/test-function"
                }
            }
        }
        self.mock_logs_client.describe_log_groups.return_value = {
            "logGroups": [{"logGroupName": "/aws/lambda/test-function"}]
        }
        
        result = self.service.aws_cloudwatch_log_group(resource)
        
        self.assertEqual(result, "/aws/lambda/test-function")

    def test_aws_cloudwatch_log_group_not_found(self):
        """Test aws_cloudwatch_log_group when log group doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "/aws/lambda/test-function"
                }
            }
        }
        self.mock_logs_client.describe_log_groups.return_value = {
            "logGroups": []
        }
        
        result = self.service.aws_cloudwatch_log_group(resource)
        
        self.assertIsNone(result)

    def test_aws_cloudwatch_event_rule_success(self):
        """Test aws_cloudwatch_event_rule with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-rule"
                }
            }
        }
        self.mock_events_client.list_rules.return_value = {
            "Rules": [{"Name": "test-rule"}]
        }
        
        result = self.service.aws_cloudwatch_event_rule(resource)
        
        self.assertEqual(result, "test-rule")

    def test_aws_cloudwatch_event_rule_not_found(self):
        """Test aws_cloudwatch_event_rule when rule doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-rule"
                }
            }
        }
        self.mock_events_client.list_rules.return_value = {
            "Rules": []
        }
        
        result = self.service.aws_cloudwatch_event_rule(resource)
        
        self.assertIsNone(result)

    def test_aws_cloudwatch_log_metric_filter_success(self):
        """Test aws_cloudwatch_log_metric_filter with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-filter",
                    "log_group_name": "/aws/lambda/test-function"
                }
            }
        }
        self.mock_logs_client.describe_metric_filters.return_value = {
            "metricFilters": [{"filterName": "test-filter"}]
        }
        
        result = self.service.aws_cloudwatch_log_metric_filter(resource)
        
        self.assertEqual(result, "/aws/lambda/test-function:test-filter")

    def test_aws_cloudwatch_log_metric_filter_not_found(self):
        """Test aws_cloudwatch_log_metric_filter when filter doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-filter",
                    "log_group_name": "/aws/lambda/test-function"
                }
            }
        }
        self.mock_logs_client.describe_metric_filters.return_value = {
            "metricFilters": []
        }
        
        result = self.service.aws_cloudwatch_log_metric_filter(resource)
        
        self.assertIsNone(result)

    def test_aws_cloudwatch_query_definition_success(self):
        """Test aws_cloudwatch_query_definition with successful response"""
        resource = {
            "change": {
                "after": {
                    "name": "test-query"
                }
            }
        }
        self.mock_logs_client.describe_query_definitions.return_value = {
            "queryDefinitions": [{
                "name": "test-query",
                "queryDefinitionId": "12345678-1234-1234-1234-123456789012"
            }]
        }
        
        result = self.service.aws_cloudwatch_query_definition(resource, self.mock_session)
        
        expected_arn = "arn:aws:logs:us-east-1:123456789012:query-definition:12345678-1234-1234-1234-123456789012"
        self.assertEqual(result, expected_arn)

    def test_aws_cloudwatch_query_definition_not_found(self):
        """Test aws_cloudwatch_query_definition when query doesn't exist"""
        resource = {
            "change": {
                "after": {
                    "name": "test-query"
                }
            }
        }
        self.mock_logs_client.describe_query_definitions.return_value = {
            "queryDefinitions": []
        }
        
        result = self.service.aws_cloudwatch_query_definition(resource, self.mock_session)
        
        self.assertIsNone(result)

    def test_aws_cloudwatch_event_target_exception(self):
        """Test aws_cloudwatch_event_target exception handling"""
        resource = {
            "change": {
                "after": {
                    "rule": "test-rule",
                    "target_id": "test-target"
                }
            }
        }
        self.mock_events_client.list_targets_by_rule.side_effect = Exception("Test error")
        
        result = self.service.aws_cloudwatch_event_target(resource)
        
        self.assertIsNone(result)

    def test_aws_cloudwatch_log_group_missing_name(self):
        """Test aws_cloudwatch_log_group with missing name"""
        resource = {
            "change": {
                "after": {}
            }
        }
        
        result = self.service.aws_cloudwatch_log_group(resource)
        
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
