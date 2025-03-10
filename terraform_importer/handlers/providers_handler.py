from typing import List, Optional, Dict
from terraform_importer.providers.base_provider import BaseProvider
from terraform_importer.providers.aws_provider import AWSProvider
from terraform_importer.providers.bitbucket_provider import BitbucketDfraustProvider
# from terraform_importer.providers.gcp_provider import GCPProvider
from terraform_importer.handlers.json_config_handler import JsonConfigHandler
import logging

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class ProvidersHandler:
    """Handles interaction with all providers."""

    providers_full_names = {
        "registry.terraform.io/hashicorp/aws": AWSProvider,
        "registry.terraform.io/hashicorp/bitbucket": BitbucketDfraustProvider,
        # "registry.terraform.io/hashicorp/gcp": GCPProvider
    }
    
    def __init__(self, provider_config: Dict):
        """
        Initializes the handler with a list of provider instances.
        Args:
            providers (List[BaseProvider]): List of provider objects.
        """
        # self.providers = {provider.__name__: provider for provider in providers}
        stript_config = JsonConfigHandler.replace_variables(provider_config["configuration"]["provider_config"], provider_config["variables"])
        stript_config = JsonConfigHandler.simplify_references(stript_config)
        stript_config = JsonConfigHandler.simplify_constant_values(stript_config)
        # self.providers = self.init_providers(stript_config)
        # self.validate_providers()
    
    def init_providers(self, provider_config: Dict) -> Dict:
        """
        Initializes the providers based on the configuration.
        Args:
            provider_config (Dict): The configuration for the providers.
        Returns:
            Dict: A dictionary of initialized providers.
        """
        providers = {}
        for provider_name, provider_data in provider_config.items():
            provider_full_name = provider_data.get("full_name")
            if provider_full_name in self.providers_full_names:
                provider_class = self.providers_full_names[provider_full_name]
                providers[provider_name] = provider_class(provider_data, provider_name)
            else:
                global_logger.warning(f"Unhandled provider type: {provider_full_name}")
                providers[provider_name] = None
        return providers

    def validate_providers(self) -> None:
        """
        Validates that all providers implement required methods.
        """
        for provider_name, provider in self.providers.items():
            if not isinstance(provider, BaseProvider):
                raise TypeError(f"Provider {provider_name} must inherit from BaseProvider.")
    
    def run_all_resources(self, resource_list: List[Dict]) -> List[Dict[str, str]]:
        """
        Iterates through all resources and retrieves {address, id} for each resource block.
        Args:
            resource_list: List[Dict]: List of Dictionary of resources grouped by type.
        Returns:
            List[Dict[str, str]]: List of resource details (address and ID).
        """
        result_list = []
        for resource in resource_list:
            resource_type = resource['type']
            resource = self.get_resource(resource_type, resource)
            if resource:
                result_list.append(resource)
        return result_list
    
    def get_resource(self, resource_type: str, resource_block: dict) -> Optional[Dict[str, str]]:
        """
        Fetches {address, id} for a specific resource by calling the respective provider.
        Args:
            provider_name (str): Name of the provider.
            resource_block (dict): The resource block to fetch details for.
        Returns:
            Optional[Dict[str, str]]: Resource details or None if not found.
        """
        provider_name = resource_block["provider"]
        address       = resource_block['address']

        try:
            id = self.providers[provider_name].get_id(resource_type, resource_block)
        except KeyError:
            global_logger.warning(f"Provider type {provider_name} doesnt exist")
            return None
        if id:
            return {"address": address, "id": id}
        
