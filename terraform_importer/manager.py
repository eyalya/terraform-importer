from terraform_importer.providers import AWSProvider, GCPProvider, BaseProvider
from terraform_importer.handlers.providers_handler import ProvidersHandler
from terraform_importer.generators.import_block_generator import ImportBlockGenerator
from terraform_importer.importer.importer import Importer
from typing import List

class Manager:
    """Orchestrates the process of generating and importing resources."""
    
    def __init__(self, providers: List[BaseProvider], terraform_config_path: str, output_path: str):
        """
        Initializes the manager with dependencies.
        Args:
            providers (List[BaseProvider]): List of provider instances.
            terraform_config_path (str): Path to Terraform configurations.
            output_path (str): Path to save the import file.
        """
        self.providers_handler = ProvidersHandler(providers)
        self.import_block_generator = ImportBlockGenerator(terraform_config_path)
        self.importer = Importer()
        self.output_path = output_path
    
    def run(self) -> None:
        """
        Executes the full process:
        1. Extract resources.
        2. Fetch resource details.
        3. Generate import file.
        4. Validate with Terraform plan.
        5. Execute import operations.
        """
        pass