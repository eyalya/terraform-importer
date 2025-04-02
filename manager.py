from terraform_importer.handlers.terraform_handler import TerraformHandler
from terraform_importer.generators.import_block_generator import ImportBlockGenerator
from typing import List, Optional

class Manager:
    """Orchestrates the process of generating and importing resources."""
    
    def __init__(self, terraform_config_path: str, options: Optional[List[str]] = None, targets: Optional[List[str]] = None):
        """
        Initializes the manager with dependencies.
        Args:
            providers (List[BaseProvider]): List of provider instances.
            terraform_config_path (str): Path to Terraform configurations.
            output_path (str): Path to save the import file.
        """
        #self.providers_handler = ProvidersHandler(providers)
        self.tf_handler = TerraformHandler(terraform_config_path, options)
        self.import_block_generator = ImportBlockGenerator(self.tf_handler)
        # self.importer = Importer()
        #self.output_path = output_path
        self.targets = targets
    def run(self) -> None:
        """
        Executes the full process:
        1. Extract resources.
        2. Fetch resource details.
        3. Generate import file.
        4. Validate with Terraform plan.
        5. Execute import operations.
        """
        self.import_block_generator.extract_resource_list(self.targets)
        pass