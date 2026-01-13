from typing import List, Optional, Dict
from terraform_importer.providers.base_provider import BaseProvider
from terraform_importer.providers.aws.aws_provider import AWSProvider
from terraform_importer.providers.bitbucket.bitbucket_provider import BitbucketDfraustProvider
# from terraform_importer.providers.kubernetes.kubernetes_provider import KubernetesProvider
# from terraform_importer.providers.gcp.gcp_provider import GCPProvider
from terraform_importer.handlers.json_config_handler import JsonConfigHandler
import logging

class ProvidersHandler:
    """Handles interaction with all providers."""

    providers_full_names = {
        "registry.terraform.io/hashicorp/aws": AWSProvider,
        "registry.terraform.io/drfaust92/bitbucket": BitbucketDfraustProvider,
        # "registry.terraform.io/hashicorp/kubernetes": KubernetesProvider,
        # "registry.terraform.io/hashicorp/gcp": GCPProvider
    }
    
    def __init__(self, provider_config: Dict):
        """
        Initializes the handler with a list of provider instances.
        Args:
            provider_config: Dict: List of provider objects.
        """
        # self.providers = {provider.__name__: provider for provider in providers}
        #stript_config = JsonConfigHandler.replace_variables(provider_config["configuration"]["provider_config"], provider_config["variables"])
        #stript_config = JsonConfigHandler.simplify_references(stript_config)
        #stript_config = JsonConfigHandler.simplify_constant_values(stript_config)
        stript_config = JsonConfigHandler.edit_provider_config(provider_config)
        self.logger = logging.getLogger(__name__)
        self.providers = self.init_providers(stript_config)
        # self.validate_providers()
    
    def init_providers(self, provider_config: Dict) -> Dict:
        """
        Initializes the ProvidersHandler instance and sets up the provider instances
        based on the provided configuration.
        Args:
            provider_config (Dict): A dictionary containing the configuration for the providers.
        Returns:
            Dict: A dictionary of initialized providers.
        """
        providers = {}
        for provider_name, provider_data in provider_config.items():
            provider_full_name = provider_data.get("full_name")
            if provider_full_name in self.providers_full_names and "expressions" in provider_data:
                provider_class = self.providers_full_names[provider_full_name]
                providers[provider_name] = provider_class(provider_data, provider_name)
            else:
                self.logger.warning(f"Unhandled provider type: {provider_full_name}")
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
            if self.providers[provider_name]:
                id = self.providers[provider_name].get_id(resource_type, resource_block)
                if id:
                    return {"address": address, "id": id}
        except KeyError:
            self.logger.warning(f"Provider type {provider_name} doesnt exist")
        return None
        
