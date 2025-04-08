"""Get Github action inputs."""

import os

FORMAT_EXTENSIONS = {
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
        "exclude_mediatypes": os.environ.get("INPUT_EXCLUDE_MEDIATYPES", None),
        "distro": os.environ.get("INPUT_DISTRO"),
        "name": os.environ.get("INPUT_NAME", None),
        "version": os.environ.get("INPUT_VERSION", None),
        "merge": os.environ.get("INPUT_MERGE", "false").lower() == "true",
        "merge_hierarchical": os.environ.get(
            "INPUT_MERGE_HIERARCHICAL", "false"
        ).lower()
        == "true",
        "vuln": os.environ.get("INPUT_VULN", "false").lower() == "true",
        "vuln_output_format": os.environ.get(
            "INPUT_VULN_OUTPUT_FORMAT", "cyclonedx-json"
        ),
        "vuln_output_file": os.environ.get("INPUT_VULN_OUTPUT_FILE"),
    }
