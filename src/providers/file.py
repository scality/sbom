"""File provider for SBOM generation."""

import os
import mimetypes
import re
import logging
from typing import Dict, Any
from scanners.syft import SyftScanner
from scanners.grype import GrypeScanner
from .base import BaseProvider


class FileProvider(BaseProvider):
    """Provider for files."""

    # RPM filename pattern: name-version-release.architecture.rpm
    # Where release often contains OS info like "el8" for RHEL/CentOS 8
    RPM_PATTERN = re.compile(
        r".*[.-](?P<os_marker>el|fc|sles)(?P<version>\d+)[._-]?.*\.rpm$"
    )

    def _get_default_output_file(self, target):
        """
        ## Generate a default output filename based on the target file.
        ### Args:
            target (str): The target file or directory.
        ### Returns:
            str: The default output filename.
        """

        if os.path.isdir(target):
            # If the target is a directory, return the directory name
            return os.path.basename(os.path.normpath(target))

        return os.path.splitext(os.path.basename(target))[0]

    def _get_rpm_info(self, rpm_path):
        """
        ## Extract OS information from RPM file.
        ### Args:
            rpm_path (str): The path to the RPM file.
        ### Returns:
            dict: A dictionary containing OS information.
        """
        info = {"is_rpm": False, "os_name": None, "os_version": None}

        mime_type, _ = mimetypes.guess_type(rpm_path)
        if mime_type != "application/x-redhat-package-manager":
            return info

        info["is_rpm"] = True

        filename = os.path.basename(rpm_path)
        match = self.RPM_PATTERN.match(filename)
        if match:
            os_marker = match.group("os_marker")
            os_version = match.group("version")

            # distros are available here: https://pkg.go.dev/github.com/anchore/grype/grype/distro
            # since rocky linux is linked to rhel in grype, we will use rhel for now
            if os_marker == "el":
                info["os_name"] = "rhel"
                info["os_version"] = os_version

        # Always return info at the end, no conditional returns inside if-blocks
        return info

    def sbom(self, inputs: Dict[str, Any] = None) -> str:
        """
        ## Scan a file target.
        ### Args:
            inputs (Dict[str, Any]): Inputs from the provider
        ### Returns:
            str: Path to the generated SBOM file
        """
        # Prepare args for the scanner with just metadata
        scanner_args = {
            "name": self.inputs.get("name"),
            "target_metadata": {
                "is_directory": os.path.isdir(self.target),
                "basename": os.path.basename(os.path.normpath(self.target)),
            },
        }

        result = SyftScanner().scan(self.target, scanner_args)

        if not result.get("success", False):
            raise RuntimeError(f"Scan failed: {result.get('error', 'Unknown error')}")

        return result

    def vuln(self, sbom_result):
        """
        ## Run vulnerability scan on a file target.
        ### Args:
            sbom_result (Dict[str, Any]): The result of the SBOM scan
        ### Returns:
            Dictionary with vulnerability scan result
        """

        if not sbom_result:
            raise ValueError("SBOM file is required for vulnerability scanning.")

        sbom_path = sbom_result.get("sbom_path")
        target_path = sbom_result.get("target")

        if not sbom_path or not os.path.exists(sbom_path):
            raise ValueError(f"SBOM file not found at {sbom_path}")

        # Initialize scanner_args
        scanner_args = {}

        # Get information about the file for distro context
        if target_path:
            rpm_info = self._get_rpm_info(target_path)

            # Add distro info if available from RPM
            if rpm_info.get("os_name") and rpm_info.get("os_version"):
                scanner_args["distro"] = rpm_info["os_name"]
                scanner_args["distro_version"] = rpm_info["os_version"]
                print(
                    f"Detected RPM for {rpm_info['os_name']} {rpm_info['os_version']}"
                )
                logging.info(
                    "Detected RPM for %s %s",
                    rpm_info["os_name"],
                    rpm_info["os_version"],
                )

        result = GrypeScanner().scan(sbom_path, scanner_args)
        if not result.get("success", False):
            raise RuntimeError(
                f"Vulnerability scan failed: {result.get('error', 'Unknown error')}"
            )

        return result
