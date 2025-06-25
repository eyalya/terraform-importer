import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from terraform_importer.providers.bitbucket_provider import BitbucketDfraustProvider
from terraform_importer.handlers.providers_handler import ProvidersHandler


import unittest
from unittest.mock import patch, MagicMock
import requests
from terraform_importer.providers.bitbucket_provider import BitbucketDfraustProvider

@patch.object(BitbucketDfraustProvider, 'run_command')  # Class-level patch
class TestBitbucketDfraustProvider(unittest.TestCase):

    def setUp(self):
        """Set up test environment"""
        self.auth_config = {
            "expressions": {
                "username": "testuser",
                "password": "testpassword"
            }
        }

    def test_init(self, mock_run_command):
        """Test __init__() to verify attribute initialization"""
        mock_run_command.return_value = MagicMock(status_code=200)  # Ensure auth check passes

        provider = BitbucketDfraustProvider(self.auth_config)

        self.assertEqual(provider.__name__, "bitbucket")
        self.assertEqual(provider.username, "testuser")
        self.assertEqual(provider.password, "testpassword")
        self.assertEqual(provider.base_url, "https://api.bitbucket.org/2.0/repositories/")
        self.assertEqual(provider.auth, ("testuser", "testpassword"))
        self.assertEqual(provider.headers, {"Accept": "application/json"})
        mock_run_command.assert_called_once_with(provider.base_url)

    def test_init_with_invalid_auth_config(self, mock_run_command):
        """Test __init__() with invalid auth config (should raise ValueError)"""
        mock_run_command.return_value = MagicMock(status_code=401, reason="Unauthorized")

        with self.assertRaises(ValueError) as context:
            BitbucketDfraustProvider({"expressions": {"username": "", "password": ""}})

        self.assertIn("Authentication failed: 401 - Unauthorized", str(context.exception))

    ###### Test check_auth() #######

    def test_check_auth_success(self, mock_run_command):
        """Test check_auth() when authentication succeeds"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_run_command.return_value = mock_response

        provider = BitbucketDfraustProvider(self.auth_config)
        mock_run_command.assert_called_once_with(provider.base_url)

    def test_check_auth_failure(self, mock_run_command):
        """Test check_auth() when authentication fails (e.g., 401 Unauthorized)"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.reason = "Unauthorized"
        mock_run_command.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            BitbucketDfraustProvider(self.auth_config)

        self.assertIn("Authentication failed: 401 - Unauthorized", str(context.exception))
        

    def test_check_auth_exception(self, mock_run_command):
        """Test check_auth() when a request exception occurs"""
        mock_run_command.side_effect = requests.RequestException("Network error")
    
        with self.assertRaises(ValueError) as context:
            BitbucketDfraustProvider(self.auth_config)  # This calls check_auth()
    
        # Verify the error message
        self.assertEqual(str(context.exception), "Authentication check failed: Network error")
    
    ########### test get_variable_uuid ##########
    
    @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.get_all_results")
    def test_get_variable_uuid_found(self, mock_get_all_results, mock_run_command):
        """Test get_variable_uuid when variable is found."""
        #mock_check_auth = MagicMock()
        #mock_check_auth.status_code = 200  # Mocking a successful authentication
        #mock_check_auth.reason = "OK"
        mock_run_command.return_value = MagicMock(status_code=200, reason="OK")
        # Mock API response with the variable present
        mock_get_all_results.return_value = [
            {"key": "VAR1", "uuid": "1234-uuid-5678"},
            {"key": "TARGET_VAR", "uuid": "abcd-uuid-efgh"},
            {"key": "VAR2", "uuid": "5678-uuid-9101"},
        ]

        provider = BitbucketDfraustProvider(self.auth_config)
        result = provider.get_variable_uuid("repo-name", "TARGET_VAR")

        self.assertEqual(result, "abcd-uuid-efgh")
        mock_get_all_results.assert_called_once_with(
            provider.list_deployment_variables_uuid, "repo-name", deployment_uuid=None
        )

    @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.get_all_results")
    def test_get_variable_uuid_not_found(self, mock_get_all_results, mock_run_command):
        """Test get_variable_uuid when variable is not found."""

        mock_run_command.return_value = MagicMock(status_code=200, reason="OK")
        # Mock API response without the variable
        mock_get_all_results.return_value = [
            {"key": "VAR1", "uuid": "1234-uuid-5678"},
            {"key": "VAR2", "uuid": "5678-uuid-9101"},
        ]

        provider = BitbucketDfraustProvider(self.auth_config)
        result = provider.get_variable_uuid("repo-name", "MISSING_VAR")

        self.assertIsNone(result)
        mock_get_all_results.assert_called_once()

    @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.get_all_results")
    def test_get_variable_uuid_empty_list(self, mock_get_all_results, mock_run_command):
        """Test get_variable_uuid when API returns an empty list."""

        mock_run_command.return_value = MagicMock(status_code=200, reason="OK")
        mock_get_all_results.return_value = []

        provider = BitbucketDfraustProvider(self.auth_config)
        result = provider.get_variable_uuid("repo-name", "ANY_VAR")

        self.assertIsNone(result)
        mock_get_all_results.assert_called_once()

    #@patch("terraform_importer.providers.bitbucket_provider.global_logger") TODO: create test after modify exception in the function!
    #@patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.get_all_results")
    #def test_get_variable_uuid_keyerror(self, mock_get_all_results, mock_logger, mock_run_command):
    #    """Test get_variable_uuid when API response is malformed (missing 'key' field)."""
    #    
    #    mock_run_command.return_value = MagicMock(status_code=200, reason="OK")
    #    mock_get_all_results.return_value = [
    #        {"wrong_key": "VAR1", "uuid": "1234-uuid-5678"},
    #        {"wrong_key": "VAR2", "uuid": "5678-uuid-9101"},
    #    ]
#
    #    provider = BitbucketDfraustProvider(self.auth_config)
    #    result = provider.get_variable_uuid("repo-name", "VAR1")
#
    #    self.assertIsNone(result)
    #    mock_logger.error.assert_called()  # Ensure logging happens for the error

    ########### test list_deployment_variables_uuid ##############

    @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth")
    def test_list_deployment_variables_uuid_success(self,mock_check_auth, mock_run_command):
        """Test list_deployment_variables_uuid when API call is successful"""
        
        mock_check_auth.return_value = MagicMock(status_code=200, reason="OK")

        # Sample API response mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"key": "VAR1", "uuid": "1234-uuid-5678"}]
        mock_run_command.return_value = mock_response
        # Create an instance of the provider
        provider = BitbucketDfraustProvider(self.auth_config)
        with patch.object(provider.logger, "debug") as mock_logger_debug:
             # Call the method
             result, url = provider.list_deployment_variables_uuid("repo-name", "deployment-uuid")
     
             # Assert that the result is as expected
             self.assertEqual(len(result), 1)
             self.assertEqual(result[0]["key"], "VAR1")
             self.assertEqual(result[0]["uuid"], "1234-uuid-5678")
     
             # Assert that the URL was correctly constructed
             self.assertEqual(url, "https://api.bitbucket.org/2.0/repositories/repo-name/deployments_config/environments/deployment-uuid/variables?page=0")
             
             # Ensure the logger was used for debug purposes
             mock_logger_debug.assert_any_call("Get Variables")
    
    @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth")
    def test_list_deployment_variables_uuid_error(self, mock_check_auth, mock_run_command):
        """Test list_deployment_variables_uuid when API call fails (non-200 status code)"""

        mock_check_auth.return_value = MagicMock(status_code=200, reason="OK")
        
        # Simulate an error response from the API
        mock_response = MagicMock()
        mock_response.status_code = 400  # Bad request
        mock_response.reason = "Bad Request"
        mock_run_command.return_value = mock_response

        # Create an instance of the provider
        provider = BitbucketDfraustProvider(self.auth_config)
        with patch.object(provider.logger, "error") as mock_logger_error:
             # Call the method
             result, url = provider.list_deployment_variables_uuid("repo-name", "deployment-uuid")
     
             # Assert that the result is None when the request fails
             self.assertIsNone(result)
             self.assertIsNone(url)
     
             # Ensure that the error was logged
             mock_logger_error.assert_called_with("Request failed: 400 - Bad Request")

    @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth")
    def test_list_deployment_variables_uuid_exception(self,mock_check_auth, mock_run_command):
        """Test list_deployment_variables_uuid when an exception is raised"""
        
        mock_check_auth.return_value = MagicMock(status_code=200, reason="OK")
        # Simulate an exception in run_command (e.g., network issue)
        mock_run_command.side_effect = requests.RequestException("Network error")

        # Create an instance of the provider
        provider = BitbucketDfraustProvider(self.auth_config)
        with patch.object(provider.logger, "error") as mock_logger_error:
             # Call the method
             result, url = provider.list_deployment_variables_uuid("repo-name", "deployment-uuid")
     
             # Assert that the result is None and the URL is None when an exception occurs
             self.assertIsNone(result)
     
             # Ensure that the exception was logged
             mock_logger_error.assert_called_with("Request failed: Network error")

    ########### test get_deployment_uuid ##########

    @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth")
    def test_get_deployment_uuid_success(self,mock_check_auth, mock_run_command):
        """Test get_deployment_uuid when deployment is found"""

        mock_check_auth.return_value = MagicMock(status_code=200, reason="OK")
        # Mock the response to simulate a successful API call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "values": [
                {"slug": "deployment-1", "uuid": "uuid-1234"},
                {"slug": "deployment-2", "uuid": "uuid-5678"}
            ]
        }
        mock_run_command.return_value = mock_response
        
        provider = BitbucketDfraustProvider(self.auth_config)
        result = provider.get_deployment_uuid("repo-name", "deployment-1")
        
        self.assertEqual(result, "uuid-1234")  # Check if the correct UUID was returned

    @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth")
    def test_get_deployment_uuid_not_found(self,mock_check_auth, mock_run_command):
        """Test get_deployment_uuid when deployment is not found"""

        mock_check_auth.return_value = MagicMock(status_code=200, reason="OK")
        # Mock the response to simulate a successful API call with no matching deployment
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "values": [
                {"slug": "deployment-1", "uuid": "uuid-1234"},
                {"slug": "deployment-2", "uuid": "uuid-5678"}
            ]
        }
        mock_run_command.return_value = mock_response
        
        provider = BitbucketDfraustProvider(self.auth_config)
        result = provider.get_deployment_uuid("repo-name", "deployment-xyz")  # Non-existent deployment
        
        self.assertIsNone(result)  # Should return None since the deployment isn't found

    @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth")
    def test_get_deployment_uuid_exception(self,mock_check_auth, mock_run_command):
        """Test get_deployment_uuid when an exception is raised"""

        mock_check_auth.return_value = MagicMock(status_code=200, reason="OK")
        # Simulate an exception in run_command (e.g., network issue)
        mock_run_command.side_effect = requests.RequestException("Network error")
        
        provider = BitbucketDfraustProvider(self.auth_config)
        with patch.object(provider.logger, "error") as mock_logger_error:
             result = provider.get_deployment_uuid("repo-name", "deployment-1")
             
             # Assert that the result is None when an exception occurs
             self.assertIsNone(result)
     
             # Ensure that the exception was logged
             mock_logger_error.assert_called_with("Request failed: Network error")

    @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth")
    def test_get_deployment_uuid_invalid_response(self, mock_check_auth, mock_run_command):
        """Test get_deployment_uuid when response is malformed"""

        mock_check_auth.return_value = MagicMock(status_code=200, reason="OK")
        # Mock the response with a malformed JSON or missing "values" field
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # Missing 'values' field
        mock_run_command.return_value = mock_response
        
        provider = BitbucketDfraustProvider(self.auth_config)
        result = provider.get_deployment_uuid("repo-name", "deployment-1")
        
        # Should return None due to the missing 'values' field
        self.assertIsNone(result)

    ########### test bitbucket_repository_variable ###########
    
    @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth")
    @patch.object(BitbucketDfraustProvider, 'get_variable_uuid')  # Mocking the get_variable_uuid method
    def test_bitbucket_repository_variable_success(self, mock_get_variable_uuid, mock_check_auth, mock_run_command):
        """Test bitbucket_repository_variable when UUID is found."""
        
        mock_check_auth.return_value = MagicMock(status_code=200, reason="OK")
        # Sample resource block (the input data)
        resource_block = {
            'change': {
                'after': {
                    'key': 'my-variable',
                    'repository': 'repo-name'
                }
            }
        }

        # Mock get_variable_uuid to return a valid UUID
        mock_get_variable_uuid.return_value = '1234-uuid-5678'
        
        # Create an instance of YourClass (replace with actual class name)
        provider = BitbucketDfraustProvider(self.auth_config)

        # Call the method
        result = provider.bitbucket_repository_variable(resource_block)

        # Assert that the returned string matches the expected format
        self.assertEqual(result, "repo-name/my-variable/1234-uuid-5678")
        mock_get_variable_uuid.assert_called_once_with('repo-name', 'my-variable')
    
    @patch("terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth")
    @patch.object(BitbucketDfraustProvider, 'get_variable_uuid')  # Mocking the get_variable_uuid method
    def test_bitbucket_repository_variable_not_found(self, mock_get_variable_uuid, mock_check_auth, mock_run_command):
        """Test bitbucket_repository_variable when UUID is not found."""
        
        mock_check_auth.return_value = MagicMock(status_code=200, reason="OK")
        # Sample resource block (the input data)
        resource_block = {
            'change': {
                'after': {
                    'key': 'my-variable',
                    'repository': 'repo-name'
                }
            }
        }

        # Mock get_variable_uuid to return None (not found)
        mock_get_variable_uuid.return_value = None
        
        # Create an instance of YourClass (replace with actual class name)
        provider = BitbucketDfraustProvider(self.auth_config)

        # Call the method
        result = provider.bitbucket_repository_variable(resource_block)

        # Assert that the result is None when the UUID is not found
        self.assertIsNone(result)
        mock_get_variable_uuid.assert_called_once_with('repo-name', 'my-variable')

    ########### test get all result #########
    # TODO: need to check bitbucket api call response to mimic in the unit tests
    #
    #@patch('terraform_importer.providers.bitbucket_provider.global_logger.debug')
    #@patch('terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth')
    #def test_get_all_results(self, mock_run_command, mock_check_auth, mock_debug):
    #    """Test get_all_results to ensure it handles pagination correctly"""
    #    
    #    mock_check_auth = MagicMock()
    #    mock_check_auth.status_code = 200  # Mocking a successful authentication
    #    mock_check_auth.reason = "OK"
#
    #    # Create an instance of the class
    #    provider = BitbucketDfraustProvider(auth_config=self.auth_config)
    #    #provider.run_command = MagicMock(return_value=mock_auth_response)
    #    # Define a mock function to simulate API responses
    #    #mock_func = MagicMock(side_effect=[
    #    #    ({"values": []}, "https://api.bitbucket.org/2.0/repositories/?page=2"),
    #    #    ({"values": [{"id": 1}, {"id": 2}]}, "https://api.bitbucket.org/2.0/repositories/?page=3"),
    #    #    ({"values": [{"id": 3}, {"id": 4}]}, "https://api.bitbucket.org/2.0/repositories/?page=4"),
    #    #    ({"values": []}, None),  # End of pagination
    #    #])
#
    #    mock_func = MagicMock(side_effect=[
    #        # First page (empty but has a next page)
    #        ({"values": [], "next": "https://api.bitbucket.org/2.0/repositories/?page=2"}, 
    #         "https://api.bitbucket.org/2.0/repositories/?page=2"),
    #        
    #        # Second page (contains results and has a next page)
    #        ({"values": [{"id": 1}, {"id": 2}], "next": "https://api.bitbucket.org/2.0/repositories/?page=3"}, 
    #         "https://api.bitbucket.org/2.0/repositories/?page=3"),
    #        
    #        # Third page (contains results and has a next page)
    #        ({"values": [{"id": 3}, {"id": 4}], "next": "https://api.bitbucket.org/2.0/repositories/?page=4"}, 
    #         "https://api.bitbucket.org/2.0/repositories/?page=4"),
    #        
    #        # Fourth page (empty, no more pages)
    #        ({"values": [], "next": None}, None),
    #    ])
#
#
    #    # Call the get_all_results method with the mock_func
    #    results = provider.get_all_results(mock_func)
    #    print (results)
    #    print (mock_func.call_count)
    #    # Assert that the results contain all the expected items from both pages
    #    self.assertEqual(len(results), 4)
    #    self.assertEqual(results, [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}])
#
    #    # Assert that the mock_func was called the expected number of times (2 times)
    #    self.assertEqual(mock_func.call_count, 3)
#
    #    # Ensure that the pagination logic (url change) works correctly
    #    mock_func.assert_any_call()  # First call (initial API request)
    #    mock_func.assert_any_call(url="https://api.bitbucket.org/2.0/repositories/?page=2")  # Second page
    #    mock_func.assert_any_call(url="https://api.bitbucket.org/2.0/repositories/?page=3")  # Third page (empty)
#
#
    #@patch('terraform_importer.providers.bitbucket_provider.global_logger.debug') 
    #@patch('terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth')
    #def test_get_all_results_no_results(self, mock_run_command, mock_check_auth, mock_debug):
    #    """Test get_all_results when no results are returned from the API"""
    #    
    #    mock_check_auth = MagicMock()
    #    mock_check_auth.status_code = 200  # Mocking a successful authentication
    #    mock_check_auth.reason = "OK"
#
    #    # Create an instance of the class
    #    provider = BitbucketDfraustProvider(auth_config=self.auth_config)
    #    
    #    # Define a mock function to simulate no results
    #    #def mock_func(*args, **kwargs):
    #    #    return {"values": []}, "https://api.bitbucket.org/2.0/repositories/?page="
    #    mock_func = MagicMock(side_effect=[
    #        ({"values": []}, None),
    #        ({"values": []}, "https://api.bitbucket.org/2.0/repositories/?page="),
    #    ])
    #    # Call the get_all_results method with the mock_func
    #    results = provider.get_all_results(mock_func)
#
    #    # Assert that the results list is empty
    #    self.assertEqual(len(results), 0)
    #    self.assertEqual(results, [])
#
    #    # Assert that the mock_func was called once
    #    self.assertEqual(mock_func.call_count, 1)
#
    #@patch('terraform_importer.providers.bitbucket_provider.global_logger.debug')
    #@patch('terraform_importer.providers.bitbucket_provider.BitbucketDfraustProvider.check_auth')
    #def test_get_all_results_single_page(self, mock_run_command, mock_check_auth, mock_debug):
    #    """Test get_all_results when only a single page of results is returned"""
    #    mock_check_auth = MagicMock()
    #    mock_check_auth.status_code = 200  # Mocking a successful authentication
    #    mock_check_auth.reason = "OK"
#
    #    # Create an instance of the class
    #    provider = BitbucketDfraustProvider(auth_config=self.auth_config)
    #    
    #    # Define a mock function to simulate a single page of results
    #    #def mock_func(*args, **kwargs):
    #    #    return {"values": [{"id": 1}, {"id": 2}]}, "https://api.bitbucket.org/2.0/repositories/?page="
    #    mock_func = MagicMock(side_effect=[
    #        ({"values": []}, None),
    #        ({"values": [{"id": 1}, {"id": 2}]}, "https://api.bitbucket.org/2.0/repositories/?page="),
    #    ])
    #    # Call the get_all_results method with the mock_func
    #    results = provider.get_all_results(mock_func)
    #    print (results)
    #    # Assert that the results list contains the expected values
    #    self.assertEqual(len(results), 2)
    #    self.assertEqual(results, [{"id": 1}, {"id": 2}])
#
    #    # Assert that the mock_func was called once
    #    self.assertEqual(mock_func.call_count, 1)
    


if __name__ == '__main__':
    unittest.main()

