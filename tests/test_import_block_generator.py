import sys
import os
import unittest
import json
from unittest.mock import Mock, patch, call, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from terraform_importer.handlers.terraform_handler import TerraformHandler
from terraform_importer.handlers.providers_handler import ProvidersHandler
from terraform_importer.generators.import_block_generator import ImportBlockGenerator


class TestImportBlockGenerator(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
        self.mock_tf_handler = Mock(spec=TerraformHandler)
        self.mock_logger = Mock()
        self.mock_provider_handler = Mock(spec=ProvidersHandler)
        self.mock_json_handler = Mock()
        
        # create instances
        self.generator = ImportBlockGenerator(self.mock_tf_handler)
        self.generator.logger = self.mock_logger
        self.generator._provider_handler = self.mock_provider_handler
        

    def test_init(self):
        """
        Test initialization of ImportBlockGenerator.
        """
        self.assertEqual(self.generator._tf_handler, self.mock_tf_handler)
        self.assertEqual(self.generator._provider_handler, self.mock_provider_handler)

    ####### run_terraform #########

    def run_terraform(self):
           # Arrange
           targets = ["-target=module.example1", "-target=module.example2"]
           expected_targets = ["example1", "example2"]
           expected_output = {"resources": ["mock_resource"]}
           
           # Mock the Terraform handler methods
           self.mock_tf_handler.run_terraform_plan.return_value = None
           self.mock_tf_handler.run_terraform_show.return_value = expected_output
           
           # Act
           result = self.generator.run_terraform(targets)
           
           # Assert
           self.mock_logger.info.assert_any_call("Running Terraform plan...")
           self.mock_logger.info.assert_any_call("Running Terraform show...")
           self.mock_tf_handler.run_terraform_plan.assert_called_once_with(targets)
           self.mock_tf_handler.run_terraform_show.assert_called_once_with(expected_targets)
           self.assertEqual(result, expected_output)
       
    def test_run_terraform_without_targets(self):
        # Arrange
        expected_output = {"resources": ["mock_resource"]}
        
        # Mock the Terraform handler methods
        self.mock_tf_handler.run_terraform_plan.return_value = None
        self.mock_tf_handler.run_terraform_show.return_value = expected_output
        
        # Act
        result = self.generator.run_terraform()
        
        # Assert
        self.mock_logger.info.assert_any_call("Running Terraform plan...")
        self.mock_logger.info.assert_any_call("Running Terraform show...")
        self.mock_tf_handler.run_terraform_plan.assert_called_once_with(None)
        self.mock_tf_handler.run_terraform_show.assert_called_once_with(None)
        self.assertEqual(result, expected_output)
    

    ########## extract_resource_list ###########

    @patch("os.path.join", return_value="/mock/path/import-targets.tf")
    def test_extract_resource_list_with_targets(self, mock_os_join):
        # Arrange
        targets = ["aws_ec2_instance.example"]
        mock_resource_list = {
            "format_version": "1.2",
            "terraform_version": "1.9.2",
            "variables": {},
             "configuration": {
                 "provider_config":  {"provider_config": {}},
            }
        }   
        mock_import_blocks = {"imports": ["mock_import"]}
        
        self.generator.run_terraform = Mock(return_value=mock_resource_list)
        self.generator.generate_imports_from_plan = Mock(return_value=mock_import_blocks)
        self.generator.create_import_file = Mock()
        self.mock_tf_handler.get_terraform_folder.return_value = "/mock/path"
        
        # Act
        result = self.generator.extract_resource_list(targets)
        
        # Assert
        self.generator.run_terraform.assert_called_once_with(targets)
        self.generator.generate_imports_from_plan.assert_called_once_with(mock_resource_list)
        self.generator.create_import_file.assert_called_once_with(mock_import_blocks, "/mock/path/import-targets.tf")
        self.assertEqual(result, mock_import_blocks)
        
    @patch("os.path.join", return_value="/mock/path/import-all.tf")
    def test_extract_resource_list_without_targets(self, mock_os_join):
        # Arrange
        mock_resource_list = {
            "format_version": "1.2",
            "terraform_version": "1.9.2",
            "variables": {},
             "configuration": {
                 "provider_config":  {"provider_config": {}},
            }
        }   
        mock_import_blocks = {"imports": ["mock_import"]}
        
        self.generator.run_terraform = Mock(return_value=mock_resource_list)
        self.generator.generate_imports_from_plan = Mock(return_value=mock_import_blocks)
        self.generator.create_import_file = Mock()
        self.mock_tf_handler.get_terraform_folder.return_value = "/mock/path"
        
        # Act
        result = self.generator.extract_resource_list()
        
        # Assert
        self.generator.run_terraform.assert_called_once_with([])
        self.generator.generate_imports_from_plan.assert_called_once_with(mock_resource_list)
        self.generator.create_import_file.assert_called_once_with(mock_import_blocks, "/mock/path/import-all.tf")
        self.assertEqual(result, mock_import_blocks)

    def test_extract_resource_list_exception_handling(self):
        # Arrange
        self.generator.run_terraform = Mock(side_effect=Exception("Terraform error"))
        
        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.generator.extract_resource_list()
        
        self.mock_logger.error.assert_called_with("Failed to extract resource list: Terraform error")
        self.assertEqual(str(context.exception), "Terraform error") 

    ####### _get_provider_for_resource ###########

    def test_get_provider_for_valid_resource(self):
        """Test that the correct provider is returned for a valid resource."""
        resource = {"address": "aws_instance.example"}
        address_to_provider_dict = {"aws_instance.example": "registry.terraform.io/hashicorp/aws"}
        provider = self.generator._get_provider_for_resource(resource, address_to_provider_dict)
        self.assertEqual(provider, "registry.terraform.io/hashicorp/aws")

    def test_get_provider_for_resource_with_index(self):
        """Test that the function correctly removes index notation and retrieves the provider."""
        resource = {"address": "aws_instance.example[0]"}
        address_to_provider_dict = {"aws_instance.example": "registry.terraform.io/hashicorp/aws"}

        provider = self.generator._get_provider_for_resource(resource, address_to_provider_dict)
        self.assertEqual(provider, "registry.terraform.io/hashicorp/aws")

    def test_get_provider_logs_error_on_exception(self):
        """Test that an exception is logged when an error occurs."""
        resource = {"address": "aws_instance.example"}
        address_to_provider_dict = None  # This will cause an exception

        provider = self.generator._get_provider_for_resource(resource, address_to_provider_dict)
        
        self.mock_logger.error.assert_called_with("Failed to get provider for resource aws_instance.example: 'NoneType' object has no attribute 'get'")
        self.assertIsNone(provider)

    def test_get_provider_for_nonexistent_resource(self):
        """Test that None is returned if the resource is not in the mapping."""
        resource = {"address": "aws_instance.unknown"}
        address_to_provider_dict = {"aws_instance.example": "registry.terraform.io/hashicorp/aws"}

        provider = self.generator._get_provider_for_resource(resource, address_to_provider_dict)
        self.assertIsNone(provider)

    ######### generate_imports_from_plan #########

    def test_generate_imports_from_plan(self):
        """Test that only 'create' resources are processed and returned."""
        # Arrange
        self.generator._get_provider_for_resource = Mock()
        resource_list = {
            "configuration": {
                "root_module": {
                    # Simulated provider configuration (mocked)
                }
            },
            "resource_changes": [
                {
                    "address": "aws_instance.example",
                    "change": {"actions": ["create"]},
                },
                {
                    "address": "aws_s3_bucket.bucket1",
                    "change": {"actions": ["update"]},  # Should be skipped
                },
            ],
        }

        # Mock provider dictionary extraction
        self.generator._get_provider_for_resource.side_effect = lambda res, _: "aws"

        # Mock provider handler behavior
        self.mock_provider_handler.run_all_resources.return_value = [
                    {"address": "aws_instance.example" , "provider": "aws"}
                ]

        # Act
        result = self.generator.generate_imports_from_plan(resource_list)

        # Assert
        self.generator.logger.info.assert_any_call("Filtering resources for 'create' actions.")
        self.generator.logger.debug.assert_any_call("Skipping resource aws_s3_bucket.bucket1 with actions: ['update']")
        self.generator.logger.info.assert_any_call("Filtered 1 resources for import.")
        self.generator._get_provider_for_resource.assert_called_once_with(
            resource_list["resource_changes"][0], {}
        )  # Ensuring it's called only for 'create' action

        self.mock_provider_handler.run_all_resources.assert_called_once_with(
            [{"address": "aws_instance.example", "change": {"actions": ["create"]} , "provider": "aws"}]
        )  # Ensuring correct data is processed

        self.assertEqual(
            result,
            [{"address": "aws_instance.example" ,"provider": "aws"}]
        )  # Ensuring expected output

    ####### create_import_file ######

    @patch('builtins.open', new_callable=MagicMock)
    #@patch('logging.Logger')
    def test_create_import_file_success(self, mock_open):
        # Arrange
        resources = [
            {'address': 'aws_instance.example1', 'id': 'i-12345'},
            {'address': 'aws_instance.example2', 'id': 'i-67890'}
        ]
        output_path = '/path/to/output/file.tf'

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Act
        result = self.generator.create_import_file(resources, output_path)

        # Assert
        self.generator.logger.info.assert_any_call(f"Creating import file at {output_path}")
        mock_open.assert_called_once_with(output_path, 'a')
        mock_file.write.assert_any_call("# Terraform import blocks\n\n")
        mock_file.write.assert_any_call("import {\n  to = aws_instance.example1\n  id = \"i-12345\"\n}\n\n")
        mock_file.write.assert_any_call("import {\n  to = aws_instance.example2\n  id = \"i-67890\"\n}\n\n")
        self.generator.logger.info.assert_any_call("Import file successfully created.")

    def test_create_import_file_missing_key(self):
        # Arrange
        resources = [
            {'address': 'aws_instance.example1'},  # Missing 'id'
        ]
        output_path = '/path/to/output/file.tf'
        
        # Act & Assert
        with self.assertRaises(ValueError):
            self.generator.create_import_file(resources, output_path)
        
        self.generator.logger.error.assert_called_once_with("Resource missing required key: 'id'")

    @patch('builtins.open', new_callable=MagicMock)
    def test_create_import_file_io_error(self, mock_open):
        # Arrange
        resources = [
            {'address': 'aws_instance.example1', 'id': 'i-12345'},
        ]
        output_path = '/path/to/output/file.tf'

        mock_open.side_effect = IOError("Permission denied")

        with self.assertRaises(IOError):
            self.generator.create_import_file(resources, output_path)

        self.generator.logger.error.assert_called_once_with(f"Failed to write to file {output_path}: Permission denied")
