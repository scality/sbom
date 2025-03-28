"""Get Github action inputs."""

import os


def get_inputs():
    """Get the inputs from the Github action."""
    return {
        "grype_version": os.environ.get("INPUT_GRYPE_VERSION"),
        "syft_version": os.environ.get("INPUT_SYFT_VERSION"),
        "target": os.environ.get("INPUT_TARGET", "./"),
        "target_type": os.environ.get("INPUT_TARGET_TYPE", "file"),
        "output_format": os.environ.get("INPUT_OUTPUT_FORMAT", "cyclonedx-json"),
        "output_file": os.environ.get("INPUT_OUTPUT_FILE"),
        "output_dir": os.environ.get("INPUT_OUTPUT_DIR", "/tmp/sbom"),
        "exclude_mediatypes": os.environ.get("INPUT_EXCLUDE_MEDIATYPES"),
        "distro": os.environ.get("INPUT_DISTRO"),
        "name": os.environ.get("INPUT_NAME"),
        "version": os.environ.get("INPUT_VERSION"),
        "vuln": os.environ.get("INPUT_VULN", "false").lower() == "true",
        "vuln_output_format": os.environ.get("INPUT_VULN_OUTPUT_FORMAT", "json"),
        "vuln_output_file": os.environ.get("INPUT_VULN_OUTPUT_FILE"),
    }


def get_output_file_extension(desired_format):
    """Get the output file extension for the given format
    Args:
        format (str): The format to get the extension for
    Returns:
        str: The file extension for the given format
    """
    format_extensions = {
        "json": "json",
        "table": "txt",
        "sarif": "sarif",
        "html": "html",
        "cyclonedx": "xml",
        "cyclonedx-json": "json",
        "spdx-json": "json",
        "junit": "xml",
        "csv": "csv",
    }
    return format_extensions.get(desired_format, "json")
