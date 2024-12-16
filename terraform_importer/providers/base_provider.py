from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging

# Define a global logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_logger = logging.getLogger("GlobalLogger")

# Abstract Base Class for Providers
class BaseProvider(ABC):
    """Abstract base class for all providers."""

    def __init__(self):
        """
        Initializes the Base Provider with required attributes.
        """
        self._resources_dict = {}
    
    def get_id(self, resource_type: str, resource_block: Dict) -> Optional[str]:
        """
        Fetches the ID for a specific resource type and resource block.
        Args:
            resource_type (str): The type of the resource (e.g., 'aws_instance').
            resource_block (Dict): The resource configuration block.
        Returns:
            Optional[str]: Resource ID if found, or None if not found.
        """
        if hasattr(self, resource_type):
            method = getattr(self, resource_type)
            return method(resource_block)
        else:
            global_logger.info(f"No such resource_type: {resource_type}")
            return None
    