"""Base provider class for all providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseProvider(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class for all providers."""

    def __init__(self, inputs: Dict[str, Any]):
        """
        ## Initialize with common provider attributes
        ### Args:
            inputs (Dict[str, Any]): Inputs from the provider
        """
        self.inputs = inputs
        self.output_dir = inputs.get("output_dir", "/tmp/sbom")
        self.name = inputs.get("name")
        self.version = inputs.get("version")
        self.target = inputs.get("target", "./")

    @abstractmethod
    def sbom(self, inputs) -> str:
        """
        ## Scan the target and generate an SBOM
        ### Returns:
            Path to the generated SBOM file
        """
