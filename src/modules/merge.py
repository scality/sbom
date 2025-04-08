"""Module for merging generated SBOMs into a single file"""

import os
import subprocess
import logging
from config.inputs import get_inputs


def extract_sbom_paths(scan_results):
    """
    ## Extract all SBOM file paths from scan results.

    Handles complex nested structures from ISO scans with multiple container images.

    ### Args:
        scan_results: Scan results dictionary or string path
    ### Returns:
        list: List of SBOM file paths
    """
    sbom_paths = []

    # If the result is already a string path
    if isinstance(scan_results, str):
        return [scan_results]

    # If it's a dictionary with results
    if isinstance(scan_results, dict):
        # Top-level SBOM path
        if "sbom_path" in scan_results:
            sbom_paths.append(scan_results["sbom_path"])

        # Handle nested container images in ISO scan results
        if "images_scan" in scan_results and "results" in scan_results.get(
            "images_scan", {}
        ):
            # Extract paths from each image result
            for image_result in scan_results["images_scan"]["results"].values():
                if isinstance(image_result, dict) and "sbom_path" in image_result:
                    sbom_paths.append(image_result["sbom_path"])

    return sbom_paths


def extract_sbom_name(scan_results):
    """
    ## Extract parent SBOM name paths from scan results.

    Handles complex nested structures from ISO scans with multiple container images.

    ### Args:
        scan_results: Scan results dictionary or string path
    ### Returns:
        list: List of SBOM names
    """
    sbom_name = []

    # If the result is already a string path
    if isinstance(scan_results, str):
        return [scan_results]

    # If it's a dictionary with results
    if isinstance(scan_results, dict):
        # Top-level SBOM path
        if "name" in scan_results:
            sbom_name.append(scan_results["name"])

    return sbom_name


def extract_sbom_version(scan_results):
    """
    ## Extract parent SBOM version paths from scan results.

    Handles complex nested structures from ISO scans with multiple container images.

    ### Args:
        scan_results: Scan results dictionary or string path
    ### Returns:
        string: SBOM version
    """
    # If the result is already a string path
    if isinstance(scan_results, str):
        return scan_results

    # If it's a dictionary with results
    if isinstance(scan_results, dict):
        # Top-level SBOM path
        if "version" in scan_results:
            return scan_results["version"]

    return ""


def merge_sbom_files(scan_results, output_file):
    """
    ## Merge multiple SBOM files into a single file with cyclondex-cli.
    ### Args:
        scan_results: Scan results (can be dictionary or list of file paths)
        output_file (str): Path to the output merged SBOM file
    ### Returns:
        str: Path to the merged SBOM file
    """
    # Get the inputs from the Github action
    inputs = get_inputs()

    # Extract SBOM paths
    if isinstance(scan_results, (dict, str)):
        sbom_paths = extract_sbom_paths(scan_results)
    else:
        sbom_paths = scan_results

    if not sbom_paths:
        raise ValueError("No SBOM files found in scan results.")

    # Extract SBOM name - get a string, not a list
    if isinstance(scan_results, (dict, str)):
        name_list = extract_sbom_name(scan_results)
        sbom_name = name_list[0] if name_list else "undefined"
    else:
        sbom_name = "undefined"

    # Extract SBOM version - get a string, not a list
    if isinstance(scan_results, (dict, str)):
        sbom_version = extract_sbom_version(scan_results)
        if not sbom_version:
            sbom_version = "undefined"
    else:
        sbom_version = "undefined"

    logging.info("Found %d SBOM files to merge", len(sbom_paths))

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Check if cyclonedx-cli is installed
    try:
        subprocess.run(
            ["cyclonedx-cli", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error(
            "cyclonedx-cli is not installed. Please install it to merge SBOM files."
        )
        raise

    # Create the command to merge SBOM files
    command = [
        "cyclonedx-cli",
        "merge",
    ]
    if inputs.get("merge_hierarchical"):
        command.append("--hierarchical")
    command.extend(
        [
            "--output-file",
            output_file,
            "--name",
            sbom_name,
            "--version",
            sbom_version,
            "--input-files",
        ]
    )

    # Add all input files
    command.extend(sbom_paths)

    try:
        logging.info("Running command: %s", " ".join(command))
        _ = subprocess.run(command, check=True, capture_output=True, text=True)
        logging.info(
            "Merged %d SBOM files successfully into %s", len(sbom_paths), output_file
        )
        return output_file  # Return the output file path, not command output
    except subprocess.CalledProcessError as e:
        logging.error("Failed to merge SBOM files: %s", e)
        logging.error("Command output: %s", e.stderr)
        raise
