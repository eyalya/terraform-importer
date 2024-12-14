from typing import List, Optional, Dict
from terraform_importer.handlers.terraform_handler import TerraformHandler
from terraform_importer.handlers.providers_handler import ProvidersHandler

class ImportBlockGenerator:
    """Generates Terraform import blocks."""
    
    def __init__(self, tf_handler: TerraformHandler, provider_handler: ProvidersHandler):
        self._tf_handler = tf_handler
        self._provider_handler = provider_handler
    
    def extract_resource_list(self, targets=[]) -> Dict[str, list]:
        self._tf_handler.run_terraform_plan(targets)
        resource_list = self._tf_handler.run_terraform_show(targets)
        import_blocks = self.generate_imports_from_plan(resource_list)
        output_file = f"{self._tf_handler.get_terraform_folder()}/import.tf"
        self.create_import_file(import_blocks, output_file)
    
    def generate_imports_from_plan(self, resource_list: Dict):
        import_blocks = []
        targets = []

        # Extract resource changes
        for resource in resource_list.get('resource_changes', []):
            if "create" not in resource['change']['actions']:
                continue
            import_blocks.append(resource)
        
        return self._provider_handler.run_all_resources(import_blocks)

    
    def create_import_file(self, resources: List[Dict[str, str]], output_path: str) -> None:
        """
        Creates an import file for the resources.
        Args:
            resources (List[Dict[str, str]]): List of resource details (address and ID).
            output_path (str): Path to save the generated import file.
        """
        import_blocks = []
        for resource in resources:
            import_blocks.append(f"import {{\n  to = {resource["address"]}\n id = \"{resource["id"]}\"\n}}")
        
        with open(output_path, 'a') as f:
            f.write("# Terraform import blocks\n\n")
            for block in import_blocks:
                f.write(block + "\n\n")
                