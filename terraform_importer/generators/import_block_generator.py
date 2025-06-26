from typing import List, Optional, Dict
from terraform_importer.handlers.terraform_handler import TerraformHandler
from terraform_importer.handlers.providers_handler import ProvidersHandler
import os
import json
import logging
import re
from terraform_importer.handlers.json_config_handler import JsonConfigHandler

class ImportBlockGenerator:
    """Generates Terraform import blocks.

    This class is responsible for:
    - Extracting resources from Terraform plans and shows.
    - Filtering resources that require imports based on their planned actions.
    - Generating and saving Terraform import blocks into a file.

    Attributes:
        _tf_handler (TerraformHandler): Handler for Terraform operations like plan and show.
        _provider_handler (ProvidersHandler): Handler for provider-specific resource actions.
    """
    
    def __init__(self, tf_handler: TerraformHandler):
        """
        Initializes the ImportBlockGenerator with Terraform and Provider handlers.
        
        Args:
            tf_handler (TerraformHandler): An instance of TerraformHandler for Terraform operations.
            provider_handler (ProvidersHandler): An instance of ProvidersHandler for provider resource handling.
        """
        self._tf_handler = tf_handler
        self._provider_handler = None
        self.logger = logging.getLogger(__name__)

    def run_terraform(self, targets: Optional[List[str]] = None) -> Dict[str, list]:
        """
        Executes Terraform plan and show commands to extract resource information.

        Args:
            targets (Optional[List[str]]): A list of Terraform resource targets to limit the scope
                                         of the plan and show commands. If None, all resources
                                         will be included.

        Returns:
            Dict[str, list]: A dictionary containing the parsed output from Terraform show,
                            including resource changes and configuration details.

        Note:
            This method first runs 'terraform plan' to generate the plan file, then
            'terraform show' to extract detailed resource information from that plan.
        """
        # Run Terraform plan and show to extract resource information
        self.logger.info("Running Terraform plan...")
        self._tf_handler.run_terraform_plan(targets)
        if targets is not None:
            targets=[t.replace("-target=module.", "") for t in targets]
        self.logger.info("Running Terraform show...")
        return self._tf_handler.run_terraform_show(targets)
        
    
    def load_resource_list_from_file(self, file_path: str) -> Dict[str, list]:
        """
        Loads a resource list from a file.
        """
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def extract_resource_list(self, targets: Optional[List[str]] = None) -> Dict[str, list]:
        """
        Extracts a list of resources from Terraform plan and show, generates import blocks, 
        and writes them to a file.

        Args:
            targets (Optional[List[str]]): A list of Terraform target resource addresses to limit the scope.

        Returns:
            Dict[str, list]: A dictionary containing resource details.
        """
        targets     = targets or []
        self.logger.info(f"Starting resource extraction for targets: {targets}")
        
        try:
            # Run Terraform plan and show to extract resource information
            resource_list = self.run_terraform(targets)
            
            self._provider_handler = ProvidersHandler(resource_list)
            
            # Generate import blocks from the resource list
            self.logger.info("Generating import blocks...")
            import_blocks = self.generate_imports_from_plan(resource_list)
            
            # Determine output file path
            output_file = os.path.join(self._tf_handler.get_terraform_folder(), f"import-{targets}.tf")
            self.logger.info(f"Saving import blocks to {output_file}")
            
            # Create the import file
            self.create_import_file(import_blocks, output_file)
            
            return import_blocks
        except Exception as e:
            self.logger.error(f"Failed to extract resource list: {e}")
            raise

    def _get_provider_for_resource(self, resource: Dict, address_to_provider_dict: Dict) -> Optional[str]:
        """
        Extracts the provider configuration key for a given resource.

        Args:
            resource (Dict): The resource to find the provider for
            address_to_provider_dict (Dict): A dictionary mapping resource addresses to their provider config keys

        Returns:
            Optional[str]: The provider config key if found, None otherwise
        """
        
        address = re.sub(r'\[\d+\]|\["[^"]+"\]', '', resource['address'])
        try:
            provider = address_to_provider_dict.get(address)
            self.logger.debug(f"Found provider {provider} for resource {address}")
            return provider
        except Exception as e:
            self.logger.error(f"Failed to get provider for resource {address}: {e}")
            return None

    def generate_imports_from_plan(self, resource_list: Dict) -> List[Dict[str, str]]:
        """
        Filters resources requiring import based on their planned actions and retrieves their IDs.

        Args:
            resource_list (Dict): The resource list extracted from Terraform show.

        Returns:
            List[Dict[str, str]]: A list of resources with their addresses and IDs.
        """
        self.logger.info("Filtering resources for 'create' actions.")
        import_blocks = []

        provider_dict = resource_list["configuration"]["root_module"]
        address_to_provider_dict = JsonConfigHandler.extract_provider_config_keys(provider_dict)

        # Extract resource changes
        for resource in resource_list.get('resource_changes', []):
            
            actions = resource['change']['actions']
            if "create" not in actions:
                self.logger.debug(f"Skipping resource {resource['address']} with actions: {actions}")
                continue
            
            provider = self._get_provider_for_resource(resource, address_to_provider_dict)
            if not provider:
                continue
            
            resource["provider"] = provider
            
            import_blocks.append(resource)
        
        self.logger.info(f"Filtered {len(import_blocks)} resources for import.")
        return self._provider_handler.run_all_resources(import_blocks)

    def create_import_file(self, resources: List[Dict[str, str]], output_path: str) -> None:
        """
        Creates an import file for the resources.

        Args:
            resources (List[Dict[str, str]]): List of resource details (address and ID).
            output_path (str): Path to save the generated import file.
        """
        self.logger.info(f"Creating import file at {output_path}")
        import_blocks = []

        for resource in resources:
            try:
                import_blocks.append(f"import {{\n  to = {resource['address']}\n  id = \"{resource['id']}\"\n}}")
            except KeyError as e:
                self.logger.error(f"Resource missing required key: {e}")
                raise ValueError(f"Invalid resource format: {resource}")
        
        # Write import blocks to the file
        try:
            with open(output_path, 'a') as f:
                f.write("# Terraform import blocks\n\n")
                for block in import_blocks:
                    f.write(block + "\n\n")
            self.logger.info("Import file successfully created.")
        except IOError as e:
            self.logger.error(f"Failed to write to file {output_path}: {e}")
            raise
