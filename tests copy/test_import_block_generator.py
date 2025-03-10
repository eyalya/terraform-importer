import unittest
from unittest.mock import Mock, patch, call
from terraform_importer.handlers.terraform_handler import TerraformHandler
from terraform_importer.handlers.providers_handler import ProvidersHandler
from terraform_importer.generators.import_block_generator import ImportBlockGenerator


class TestImportBlockGenerator(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
        self.mock_tf_handler = Mock(spec=TerraformHandler)
        self.mock_provider_handler = Mock(spec=ProvidersHandler)

        # Create instance of ImportBlockGenerator
        self.generator = ImportBlockGenerator(self.mock_tf_handler, self.mock_provider_handler)

    def test_init(self):
        """
        Test initialization of ImportBlockGenerator.
        """
        self.assertEqual(self.generator._tf_handler, self.mock_tf_handler)
        self.assertEqual(self.generator._provider_handler, self.mock_provider_handler)

    # @patch("builtins.open", new_callable=Mock)
    # def test_extract_resource_list(self, mock_open):
    #     """
    #     Test extract_resource_list workflow.
    #     """
    #     # Mock methods in TerraformHandler
    #     self.mock_tf_handler.run_terraform_plan.return_value = None
    #     self.mock_tf_handler.run_terraform_show.return_value = {"resource_changes": []}
    #     self.mock_tf_handler.get_terrafor
