from typing import List, Optional, Dict
from terraform_importer.providers.base_provider import BaseProvider

class ProvidersHandler:
    """Handles interaction with all providers."""
    
    def __init__(self, providers: List[BaseProvider]):
        """
        Initializes the handler with a list of provider instances.
        Args:
            providers (List[BaseProvider]): List of provider objects.
        """
        self.providers = {type(provider).__name__: provider for provider in providers}
        self.validate_providers()
    
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
            result_list.append(self.get_resource(resource_type, resource))
        return resource_list

    
    def get_resource(self, resource_type: str, resource_block: dict) -> Optional[Dict[str, str]]:
        """
        Fetches {address, id} for a specific resource by calling the respective provider.
        Args:
            provider_name (str): Name of the provider.
            resource_block (dict): The resource block to fetch details for.
        Returns:
            Optional[Dict[str, str]]: Resource details or None if not found.
        """
        provider_name = resource_type.split("_")[0]
        address       = resource_block['address']
        id = self.providers[provider_name].get_id(resource_type, resource_block)
        if id:
            return {"address": address, "id": id}
        return None
