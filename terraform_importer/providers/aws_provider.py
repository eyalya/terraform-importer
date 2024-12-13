from terraform_importer.providers.base_provider import BaseProvider
from typing import List, Optional, Dict
from terraform_importer.providers.aws_services.base import BaseAWSService
import os
import importlib.util
import inspect
import boto3

# AWS Provider
class AWSProvider(BaseProvider):
    """AWS-specific implementation of the BaseProvider."""

    def __init__(self):
        super().__init__()
        # TODO: Change to auth config
        self.name = "aws"
        self.session = boto3.session.Session(profile_name='cordio-payer')
        
        self._resources_dict = {}

        # Discover and instantiate all subclasses of BaseAWSService
        service_classes = self.get_aws_service_subclasses(BaseAWSService, "terraform_importer/providers/aws_services")
        for service_class in service_classes:
            # Instantiate the service
            service_instance = service_class(self.session)
            self.add_to_resource_dict(service_instance)
        
    def add_to_resource_dict(self, service: BaseAWSService):
        """
        Updates the resource dictionary with resources from a service.
        Args:
            service (BaseAWSService): An instance of a service class.
        """
        self._resources_dict.update(
            {resource: service for resource in service.get_resource_list()}
        )
        
    def get_aws_service_subclasses(self, base_class, folder_path: str):
        """
        Dynamically finds all subclasses of a given base class within a folder.
        Args:
            base_class (type): The base class to search for subclasses.
            folder_path (str): Path to the folder containing modules to inspect.
        Returns:
            List[type]: A list of subclass types.
        """
        subclasses = []

        # Get all Python files in the folder
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".py") and not file_name.startswith("__"):
                module_name = file_name[:-3]  # Remove the .py extension
                module_path = os.path.join(folder_path, file_name)

                # Load the module dynamically
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Inspect the module for subclasses
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, base_class) and obj is not base_class:
                        subclasses.append(obj)

        return subclasses
    
    def get_id(self, resource_type: str, resource_block: dict) -> Optional[str]:
        return self._resources_dict[resource_type].get_id(resource_type, resource_block)


povider = AWSProvider()
