import unittest
import json
from unittest.mock import Mock, patch, call
from terraform_importer.handlers.terraform_handler import TerraformHandler
from terraform_importer.handlers.providers_handler import ProvidersHandler
from terraform_importer.generators.import_block_generator import ImportBlockGenerator


class TestImportBlockGenerator(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
        self.mock_tf_handler = Mock(spec=TerraformHandler)
        self._resource_list = json.load(open("tests/assets/plan.json"))
        # # Create instance of ImportBlockGenerator
        self.generator = ImportBlockGenerator(self.mock_tf_handler)


   
    def test_init(self):
        """
        Test initialization of ImportBlockGenerator.
        """
        self.assertEqual(self.generator._tf_handler, self.mock_tf_handler)
        self.assertEqual(self.generator._provider_handler, self.mock_provider_handler)

    @patch("terraform_importer.generators.import_block_generator.ImportBlockGenerator._get_provider_for_resource")
    def test_generate_imports_from_plan(self, mock_get_provider_for_resource):
        """
        Test generate_imports_from_plan workflow.
        """
        # Mock the run_all_resources method
        mock_get_provider_for_resource.return_value = None

        # Call the method under test
        self.generator._provider_handler = ProvidersHandler(self._resource_list)
        self.generator.generate_imports_from_plan()

        # # Assert that run_all_resources was called with the correct import blocks
        # self.mock_provider_handler.run_all_resources.assert_called_once()
        
        # # You can add more specific assertions about the import_blocks passed to run_all_resources
        # # For example:
        # actual_import_blocks = mock_run_all_resources.call_args[0][0]
        # self.assertIsInstance(actual_import_blocks, list)

    def test_extract_resource_list(self):
        """
        Test extract_resource_list workflow.
        """
        # Mock methods in TerraformHandler
        self.mock_tf_handler.run_terraform_plan.return_value = None
        self.mock_tf_handler.run_terraform_show.return_value = self._resource_list

        # Call the method under test
        result = self.generator.extract_resource_list()

        # Assert terraform commands were called
        self.mock_tf_handler.run_terraform_plan.assert_called_once()
        self.mock_tf_handler.run_terraform_show.assert_called_once()

        # Assert the result matches the expected resource list
        self.assertEqual(result, self._resource_list)

    # @patch("builtins.open", new_callable=Mock)
    # def test_extract_resource_list(self, mock_open):
    #     """
    #     Test extract_resource_list workflow.
    #     """
    #     # Mock methods in TerraformHandler
    #     self.mock_tf_handler.run_terraform_plan.return_value = None
    #     self.mock_tf_handler.run_terraform_show.return_value = {"resource_changes": []}
    #     self.mock_tf_handler.get_terrafor
