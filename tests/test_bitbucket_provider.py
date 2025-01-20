import unittest
from unittest.mock import Mock, patch
from typing import List, Dict
from terraform_importer.providers.bitbucket_provider import BitbucketDfraustProvider
from terraform_importer.handlers.providers_handler import ProvidersHandler


class TestBitbucketDfraustProvider(unittest.TestCase):
    def setUp(self):
        """
        Set up mock providers for testing.
        """
        self.bitbucket = BitbucketDfraustProvider()
        self.providers = [self.bitbucket]
        self.handler = ProvidersHandler(self.providers)
        # self.username = "test-user"
        # self.password = "test-pass"
        # self.provider = BitbucketDfraustProvider(self.username, self.password)
        


    def test_init(self):
        """
        Test initialization of ProvidersHandler.
        """
        try:
            # Attempt to initialize the class
            bitbucket = self.bitbucket
        except Exception as e:
            # Fail the test if an exception is raised
            self.fail(f"Initialization raised an exception: {e}")

    def test_get_env_variable(self):
        """
        Test Get env variable.
        """
        repository = "cordio-e2e-sv-classifier-service"
        deployment = "{054b460e-6434-4ac3-a72f-ffe7b3796595}"
        id = self.bitbucket.get_variable_uuid(repository, "ENV_SV_BUCKET_NAME", deployment)
        self.assertEqual(id, "{dace11f6-8045-4109-9824-167fefadb819}")

    def test_get_deployment_uuid(self):
        """
        Test deployment_uuid.
        """
        repository = "cordio-e2e-sv-classifier-service"
        id = self.bitbucket.get_deployment_uuid(repository, "dev1")
        self.assertEqual(id, "{054b460e-6434-4ac3-a72f-ffe7b3796595}")
    
    def test_bitbucket_deployment(self):
        """
        Test deployment_uuid.
        """
        resource = {
            "address": "module.scheduled_task_engine_pipeline[0].bitbucket_deployment.this",
            "module_address": "module.scheduled_task_engine_pipeline[0]",
            "mode": "managed",
            "type": "bitbucket_deployment",
            "name": "this",
            "provider_name": "registry.terraform.io/drfaust92/bitbucket",
            "change": {
                "actions": [
                    "create"
                ],
                "before": None,
                "after": {
                    "name": "dev1-engine",
                    "repository": "cordiodev/cordio-lambda-schedule-task",
                    "stage": "Test"
                },
                "after_unknown": {
                    "id": True,
                    "restrictions": True,
                    "uuid": True
                },
                "before_sensitive": False,
                "after_sensitive": {
                    "restrictions": []
                }
            }
        }
        
        id = self.bitbucket.bitbucket_deployment(resource)
        self.assertIsNotNone(id)

    def test_bitbucket_deployment_variable(self):
        """
        Test deployment_uuid.
        """
        
        resource = {
            "address": "module.e2e_algos[0].module.sv_classifier.module.service_pipeline.bitbucket_deployment_variable.this[\"ENV_SV_BUCKET_NAME\"]",
            "type": "bitbucket_deployment_variable",
            "change": {
                "actions": [
                    "create"
                ],
                "after": {
                    "key": "ECS_TASK_EXECUTION_ROLE_ARN",
                    "deployment": "cordiodev/codio-e2e-sv-classifier:{4e42d7a9-d41f-43ed-9a55-a01a4d40be2a}",
                    "value": "arn:aws:iam::891513744586:role/ecsTaskExecutionRole"
                },
                "after_unknown": {
                    "deployment": True,
                    "id": True,
                    "uuid": True
                },
                "before_sensitive": False,
                "after_sensitive": {
                    "value": True
                }
            }
        }
        
        id = self.bitbucket.bitbucket_deployment_variable(resource)
        self.assertIsNotNone(id)
    
    def test_bitbucket_repository_variable(self):
        """
        Test deployment_uuid.
        """
        resource = {
            "address": "module.billing_service[0].module.service_pipeline.bitbucket_repository_variable.this[\"CONTAINER_PORT\"]",
            "module_address": "module.billing_service[0].module.service_pipeline",
            "mode": "managed",
            "type": "bitbucket_repository_variable",
            "name": "this",
            "index": "CONTAINER_PORT",
            "provider_name": "registry.terraform.io/drfaust92/bitbucket",
            "change": {
                "actions": [
                    "create"
                ],
                "before": None,
                "after": {
                    "key": "CONTAINER_PORT",
                    "repository": "cordiodev/cordio-billing-service",
                    "secured": False,
                    "value": "80"
                },
                "after_unknown": {
                    "id": True,
                    "uuid": True,
                    "workspace": True
                },
                "before_sensitive": False,
                "after_sensitive": {
                    "value": True
                }
            }
        }

        id = self.bitbucket.bitbucket_repository_variable(resource)
        self.assertIsNotNone(id)
    
    # @patch("terraform_importer.providers.bitbucket_provider.requests.Session.get")
    # @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth")
    # def test_check_auth_success(self, mock_get):
    #     """
    #     Test check_auth for successful authentication.
    #     """
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_get.return_value = mock_response

    #     try:
    #         self.provider.check_auth()
    #     except Exception as e:
    #         self.fail(f"check_auth raised an exception: {e}")

    # @patch("terraform_importer.providers.bitbucket_dfraust_provider.requests.Session.get")
    # def test_check_auth_failure(self, mock_get):
    #     """
    #     Test check_auth for failed authentication.
    #     """
    #     mock_response = Mock()
    #     mock_response.status_code = 401
    #     mock_response.reason = "Unauthorized"
    #     mock_get.return_value = mock_response

    #     with self.assertRaises(ValueError) as context:
    #         self.provider.check_auth()

    #     self.assertIn("Authentication failed: 401 - Unauthorized", str(context.exception))

    # @patch("terraform_importer.providers.bitbucket_dfraust_provider.requests.Session.get")
    # def test_get_deployment_uuid_success(self, mock_get):
    #     """
    #     Test get_deployment_uuid for a successful response.
    #     """
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {
    #         "values": [{"slug": "dev1", "uuid": "test-uuid-123"}]
    #     }
    #     mock_get.return_value = mock_response

    #     uuid = self.provider.get_deployment_uuid("test-repo", "dev1")
    #     self.assertEqual(uuid, "test-uuid-123")

    # @patch("terraform_importer.providers.bitbucket_dfraust_provider.requests.Session.get")
    # def test_get_deployment_uuid_not_found(self, mock_get):
    #     """
    #     Test get_deployment_uuid when the deployment is not found.
    #     """
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {"values": []}
    #     mock_get.return_value = mock_response

    #     uuid = self.provider.get_deployment_uuid("test-repo", "nonexistent")
    #     self.assertIsNone(uuid)

    # @patch("terraform_importer.providers.bitbucket_dfraust_provider.requests.Session.get")
    # def test_list_deployment_variables_uuid(self, mock_get):
    #     """
    #     Test list_deployment_variables_uuid for successful retrieval.
    #     """
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {
    #         "values": [{"key": "test-var", "uuid": "var-uuid-123"}]
    #     }
    #     mock_get.return_value = mock_response

    #     variables, url = self.provider.list_deployment_variables_uuid(
    #         "test-repo", "deployment-uuid-123"
    #     )
    #     self.assertEqual(variables["values"][0]["uuid"], "var-uuid-123")

    # @patch("terraform_importer.providers.bitbucket_dfraust_provider.requests.Session.get")
    # def test_get_variable_uuid_success(self, mock_get):
    #     """
    #     Test get_variable_uuid for finding a variable UUID.
    #     """
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {
    #         "values": [{"key": "test-var", "uuid": "var-uuid-123"}]
    #     }
    #     mock_get.return_value = mock_response

    #     uuid = self.provider.get_variable_uuid("test-repo", "test-var", "deployment-uuid-123")
    #     self.assertEqual(uuid, "var-uuid-123")

    # @patch("terraform_importer.providers.bitbucket_dfraust_provider.requests.Session.get")
    # def test_get_variable_uuid_not_found(self, mock_get):
    #     """
    #     Test get_variable_uuid when the variable is not found.
    #     """
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {"values": []}
    #     mock_get.return_value = mock_response

    #     uuid = self.provider.get_variable_uuid("test-repo", "nonexistent-var", "deployment-uuid-123")
    #     self.assertIsNone(uuid)

    # @patch("terraform_importer.providers.bitbucket_dfraust_provider.requests.Session.get")
    # def test_get_all_results(self, mock_get):
    #     """
    #     Test get_all_results for paginated API response.
    #     """
    #     mock_response_1 = Mock()
    #     mock_response_1.status_code = 200
    #     mock_response_1.json.return_value = {"values": [{"id": 1}], "next": "page=2"}

    #     mock_response_2 = Mock()
    #     mock_response_2.status_code = 200
    #     mock_response_2.json.return_value = {"values": [{"id": 2}], "next": None}

    #     mock_get.side_effect = [mock_response_1, mock_response_2]

    #     def mock_func(*args, **kwargs):
    #         return mock_get().json.return_value, kwargs.get("url", "page=0")

    #     results = self.provider.get_all_results(mock_func)
    #     self.assertEqual(len(results), 2)
    #     self.assertEqual(results[0]["id"], 1)
    #     self.assertEqual(results[1]["id"], 2)

    # @patch("terraform_importer.providers.bitbucket_dfraust_provider.requests.Session.get")
    # def test_bitbucket_deployment(self, mock_get):
    #     """
    #     Test bitbucket_deployment for generating the import block.
    #     """
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {
    #         "values": [{"slug": "deployment-name", "uuid": "deployment-uuid-123"}]
    #     }
    #     mock_get.return_value = mock_response

    #     resource_block = {
    #         "change": {
    #             "after": {
    #                 "name": "deployment-name",
    #                 "repository": "test-repo",
    #             }
    #         }
    #     }

    #     uuid = self.provider.bitbucket_deployment(resource_block)
    #     self.assertEqual(uuid, "deployment-uuid-123")

    


if __name__ == "__main__":
    unittest.main()
