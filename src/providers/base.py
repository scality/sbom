"""Base provider class for all providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from config.inputs import get_inputs
from modules.merge import merge_sbom_files


class BaseProvider(ABC):
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
        raise NotImplementedError("Subclasses must implement this method")

    def merge(self, scan_results):
        """
        ## Merge multiple SBOMs into a single file.

        Args:
            scan_results: The scan results (can be dictionary or string)

        Returns:
            str: Path to the merged SBOM file
        """
        # Get the inputs
        inputs = get_inputs()
        output_dir = inputs.get("output_dir") or "/tmp/sbom"

        # Extract name and version from scan results
        name = "merged"
        version = "1.0.0"

        if isinstance(scan_results, dict):
            # Get name and version from the main SBOM if available
            name = scan_results.get("name", name)
            version = scan_results.get("version", version)

        # Determine output filename
        output_file = (
            inputs.get("merge_output_file")
            or f"{output_dir}/{name}_{version}_merged_sbom.json"
        )

        # Extract and merge SBOM files
        if isinstance(scan_results, str):
            scan_results = [scan_results]

        return merge_sbom_files(scan_results, output_file)
