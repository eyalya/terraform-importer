from typing import List, Optional, Dict
from terraform_importer.providers.base_provider import BaseProvider
import logging

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

class ProvidersHandler:
    """Handles interaction with all providers."""
    
    def __init__(self, provider_config: Dict):
        """
        Initializes the handler with a list of provider instances.
        Args:
            providers (List[BaseProvider]): List of provider objects.
        """
        # self.providers = {provider.__name__: provider for provider in providers}
        self.providers = self.init_providers(provider_config)
        self.validate_providers()
    
    def init_providers(self, provider_config: Dict) -> Dict:
        """
        Initializes the providers based on the configuration.
        Args:
            provider_config (Dict): The configuration for the providers.
        Returns:
            Dict: A dictionary of initialized providers.
        """
        providers = {}
        providers_config= provider_config["configuration"]["provider_config"]
        variables = provider_config["variables"]
        for provider, provider_data in providers_config.items():
            provider_name = provider  # e.g., "aws.euCentral1"
            provider_class = provider_data['name']
            modified_providers_config = self.resolve_variables(providers_config, variables)
            if provider_class == "aws":
                   provider = AWSProvider(modified_providers_config)
               elif provider_class == "bitbucket":
                   provider = BitbucketDfraustProvider(modified_providers_config)
               elif provider_class == "gcp":
                   provider = GCPProvider(modified_providers_config)
               else:
                   logger.warning(f"Unhandled provider type: {provider_class}")
                   provider = None
               providers[provider_name] = provider
            return providers

    def resolve_variables (providers_config, variables)
            #provider_full_name = provider_data["full_name"]  # e.g., "registry.terraform.io/hashicorp/aws"
            ### to improve : create function that change all ref that start with var.
            assume_role = [
                resolve_variable_reference(role_arn_ref, variables)
                for role_arn_ref in provider_data.get('expressions', {})
                .get('assume_role', [{}])[0]
                .get('role_arn', {})
                .get('references', [])
            ]
            profile = [
                resolve_variable_reference(profile_ref, variables)
                for profile_ref in provider_data.get('expressions', {})
                .get('profile', {})
                .get('references', [])
            ]
            username = [
                resolve_variable_reference(username_ref, variables)
                for username_ref in provider_data.get('expressions', {})
                .get('username', {})
                .get('references', [])
            ]
            password = [
                resolve_variable_reference(password_ref, variables)
                for password_ref in provider_data.get('expressions', {})
                .get('password', {})
                .get('references', [])
            ]
            providers_config["expressions"]["assume_role"]["role_arn"]["references"] = assume_role
            providers_config["expressions"]["profile"]["references"] = profile
            providers_config["expressions"]["username"]["references"] = username
            providers_config["expressions"]["password"]["references"] = password
            # Match provider_name to specific classes
           #return {provider.__name__: provider for provider in providers}

    def resolve_variable_reference(self, ref, variables):
        """Resolve a variable reference from the 'variables' block, only if it starts with 'var.'"""
        if ref and ref.startswith("var."):
            var_name = ref[len("var."):].strip()  # Remove the 'var.' prefix
            var_data = variables.get(var_name, {}).get("value", None)
            if var_data is None:
                logger.warning(f"Variable {var_name} not found or has no value.")
            return var_data
        return ref  # If it's not a variable reference, return the value as-is
    
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
        
