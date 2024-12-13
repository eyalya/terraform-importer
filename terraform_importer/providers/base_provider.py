from abc import ABC, abstractmethod
from typing import List, Dict, Optional


# Abstract Base Class for Providers
class BaseProvider(ABC):
    """Abstract base class for all providers."""
    
    @abstractmethod
    def get_id(self, resource_type: str, resource_block: dict) -> Optional[str]:
        """
        Fetches the resource ID for a given resource block.
        Args:
            resource_type (str): Type of the resource (e.g., "aws_instance").
            resource_block (dict): Configuration block for the resource.
        Returns:
            Optional[str]: Resource ID if found, else None.
        """
        pass
    
    # @abstractmethod
    # def get_supported_resources(self) -> List[str]:
    #     """
    #     Returns a list of supported resource types for the provider.
    #     Returns:
    #         List[str]: Supported resource types (e.g., ["aws_instance", "aws_s3_bucket"]).
    #     """
    #     pass
