"""ISO provider for SBOM generation."""

import os
import re
import pathlib
import logging
from typing import Dict, Any, Optional

import magic
from pyunpack import Archive
from scanners.syft import SyftScanner
from scanners.grype import GrypeScanner
from .base import BaseProvider
from .image import ImageProvider


# Define version patterns as a constant
VERSION_PATTERNS = [r"\d+\.\d+\.\d+", r"\d+\.\d+", r"\s+\d+$"]


class IsoProvider(BaseProvider):
    """Provider for ISO scanning operations."""

    tmp_extracted_dir = "/tmp/extracted"

    def __init__(self, inputs: Dict[str, Any]):
        """
        ## Initialize ISO provider with inputs.
        ### Args:
            inputs (Dict[str, Any]): Inputs from the provider
        """
        super().__init__(inputs)
        self.iso_path = inputs.get("target")
        self.iso_info = None

    def sbom(self, inputs: Dict[str, Any] = None) -> str:
        """
        ## Scan an ISO target by extracting it and analyzing its contents.
        ### Args:
            inputs (Dict[str, Any]): Inputs from the provider
        ### Returns:
            dict: Dictionary with SBOM scan result
        """

        inputs = inputs or self.inputs
        # Validate target is a valid ISO file
        if not self._validate_iso():
            raise ValueError(f"Target is not a valid ISO file: {self.iso_path}")

        # Get ISO metadata and extract ISO
        self.iso_info = self._get_iso_info()
        extracted_dir = self._extract_iso()

        # Set up scanner args
        scanner_args = {
            "output_file": self._get_iso_filename(),
            "name": self._get_iso_name(),
            "version": self._get_iso_version(),
        }

        # Run scanner on extracted ISO contents
        logging.info("Scanning ISO contents: %s", extracted_dir)
        result = SyftScanner().scan(extracted_dir, scanner_args)

        # Check for embedded images
        images_dir = self._find_images_dir(extracted_dir)
        if not images_dir:
            logging.info("No images found in ISO, returning ISO scan results only")
            return result

        # If images found, scan them separately
        logging.info("Found images directory in ISO: %s", images_dir)

        # Return result with additional info about images
        result["has_images"] = True
        result["iso_info"] = self.iso_info
        result["extracted_dir"] = extracted_dir

        # Scan images if requested
        if self.inputs.get("scan_embedded_images", True):
            image_inputs = self.inputs.copy()
            image_inputs["target"] = images_dir
            image_inputs["output_file"] = result["sbom_path"].replace(
                ".json", "_images.json"
            )

            image_provider = ImageProvider(image_inputs)
            image_result = image_provider.sbom()
            result["images_scan"] = image_result

        return result

    def vuln(self, sbom_result):
        """
        ## Run vulnerability scan on the ISO SBOM.
        ### Args:
            sbom_result (Dict[str, Any]): The result of the SBOM scan
        ### Returns:
            Dictionary with vulnerability scan result
        """
        if not sbom_result:
            raise ValueError("SBOM result is required for vulnerability scanning")

        # Handle different result formats
        if isinstance(sbom_result, str):
            sbom_path = sbom_result
        elif isinstance(sbom_result, dict):
            sbom_path = sbom_result.get("sbom_path")
        else:
            raise ValueError(f"Unsupported SBOM result type: {type(sbom_result)}")

        if not sbom_path or not os.path.exists(sbom_path):
            raise ValueError(f"SBOM file not found at {sbom_path}")

        # Set up vulnerability scanner args
        scanner_args = {
            "output_file": sbom_path.replace(".json", "_vuln"),
        }

        # Run vulnerability scan
        logging.info("Scanning ISO SBOM for vulnerabilities: %s", sbom_path)
        result = GrypeScanner().scan(sbom_path, scanner_args)

        # If there are images, scan those SBOMs too
        if isinstance(sbom_result, dict) and sbom_result.get("images_scan"):
            image_sboms = sbom_result.get("images_scan")
            image_vuln_results = {}

            # For each image SBOM, run vulnerability scan
            if isinstance(image_sboms, dict) and "results" in image_sboms:
                for image_name, image_result in image_sboms["results"].items():
                    image_sbom_path = image_result.get("sbom_path")
                    if image_sbom_path and os.path.exists(image_sbom_path):
                        image_vuln_results[image_name] = GrypeScanner().scan(
                            image_sbom_path,
                            {"output_file": image_sbom_path.replace(".json", "_vuln")},
                        )

            result["image_vulns"] = image_vuln_results

        return result

    def _get_iso_filename(self) -> str:
        """
        ## Generate output filename for ISO SBOM.
        ### Returns:
            str: The output filename for the ISO SBOM
        """
        if self.inputs.get("output_file"):
            return self.inputs.get("output_file")

        iso_name = self._get_iso_name()
        iso_version = self._get_iso_version()

        filename = f"iso_{iso_name}"
        if iso_version:
            filename += f"_{iso_version}"

        # Return without .json extension - let the scanner add the appropriate extension
        return os.path.join(self.output_dir, filename)

    def _get_iso_name(self) -> str:
        """
        ## Get name for the ISO.
        ### Returns:
            str: The name for the ISO
        """
        # Use explicit name if provided
        if self.name:
            return self.name

        # Try to get name from volume info
        if self.iso_info and self.iso_info.get("volume_name"):
            volume_name = self.iso_info["volume_name"]

            # Try to separate name from version
            # Look for version patterns first
            for pattern in VERSION_PATTERNS:
                match = re.search(pattern, volume_name)
                if match:
                    # Extract just the name part
                    name_part = volume_name[: match.start()].strip()
                    if name_part:  # Make sure we have something before the version
                        return name_part.lower().replace(" ", "-")

            # If no version pattern found, use the whole name
            return volume_name.lower().replace(" ", "-")

        # Fall back to file basename
        return pathlib.Path(self.iso_path).stem

    def _get_iso_version(self) -> str:
        """
        ## Get version for the ISO.
        ### Returns:
            str: The version for the ISO
        """
        # Use explicit version if provided
        if self.version:
            return self.version

        # Try to extract version from volume name
        if self.iso_info and self.iso_info.get("volume_name"):
            return self._extract_version_from_iso_name(self.iso_info["volume_name"])

        return "unknown"

    def _validate_iso(self) -> bool:
        """
        ## Determine if the target is a valid ISO file.
        ### Returns:
            bool: True if valid ISO, False otherwise
        """
        if not os.path.isfile(self.iso_path):
            return False

        # Check if it's an ISO file using python-magic
        try:
            file_type = magic.from_file(self.iso_path)
            return "ISO 9660" in file_type
        except RuntimeError as error:
            logging.error("Error checking file type: %s", error)
            return False

    def _get_iso_info(self) -> Dict[str, Any]:
        """
        ## Get detailed information about an ISO file.
        ### Returns:
            Dict[str, Any]: Dictionary with ISO information
        """
        try:
            # Get file type information
            file_info = magic.from_file(self.iso_path)

            # Extract volume name if present
            # Volume name between single quotes
            # Example: "ISO 9660 CD-ROM filesystem data 'Volume Name'"
            # Split by spaces and look for the part with single quotes
            # This is a simplified approach and may not cover all cases
            # but should work for most standard ISO files
            volume_name = None
            if "'" in file_info:
                volume_name = file_info.split("'")[1]

            return {
                "file_type": file_info,
                "volume_name": volume_name,
                "path": self.iso_path,
            }
        except RuntimeError as error:
            logging.error("Error getting ISO info: %s", error)
            return {"error": str(error), "path": self.iso_path}

    def _extract_version_from_iso_name(self, volume_name: str) -> str:
        """
        ## Extract version number from ISO volume name.
        ### Args:
            volume_name (str): The volume name of the ISO
        ### Returns:
            str: The extracted version number
        """
        if not volume_name:
            return "unknown"

        # Match version patterns like x.y or x.y.z
        version_pattern = re.compile(r"(\d+\.\d+(?:\.\d+)?)")
        matches = version_pattern.findall(volume_name)

        # Return the last match if any
        if matches:
            return matches[-1]

        # Fallback: Try to extract only numbers
        numeric_pattern = re.compile(r"(\d+)")
        matches = numeric_pattern.findall(volume_name)
        if matches:
            return matches[-1]

        return "unknown"

    def _extract_iso(self) -> str:
        """
        ## Extract ISO file to a temporary directory.
        ### Returns:
            str: The path to the extracted ISO directory
        """
        iso_basename = os.path.basename(self.iso_path)
        extracted_dir = os.path.join(self.tmp_extracted_dir, "extracted", iso_basename)

        os.makedirs(os.path.dirname(extracted_dir), exist_ok=True)

        # Check if already extracted
        if os.path.exists(extracted_dir):
            logging.info("ISO already extracted at: %s", extracted_dir)
            return extracted_dir

        # Extract the ISO
        logging.info("Extracting ISO to: %s", extracted_dir)
        os.makedirs(extracted_dir, exist_ok=True)

        try:
            Archive(self.iso_path).extractall(extracted_dir)
            return extracted_dir
        except Exception as error:
            logging.error("Failed to extract ISO: %s", error)
            raise

    def _find_images_dir(self, extracted_dir: str) -> Optional[str]:
        """
        ## Find images directory in the extracted ISO.
        ### Args:
            extracted_dir (str): The path to the extracted ISO directory
        ### Returns:
            str: The path to the images directory, or None if not found
        """
        # Check if image directory is present directly
        image_dir = os.path.join(extracted_dir, "images")
        if os.path.isdir(image_dir):
            return image_dir

        # Check for images directory in subdirectories
        for root, dirs, _ in os.walk(extracted_dir):
            if "images" in dirs:
                return os.path.join(root, "images")

        return None
