"""Syft scanner implementation."""  # pylint: disable=cyclic-import

import os
import subprocess
import logging
from config.inputs import get_inputs, get_output_file_extension


class SyftScanner:
    """Scanner implementation for Syft."""

    def configure_syft(self):
        """
        ## Configure the Syft scanner
        ### This method sets the environment variables required for Syft to run.
        """

        os.environ["SYFT_FORMAT_PRETTY"] = "true"
        os.environ["SYFT_SCOPE"] = "all-layers"
        os.environ["SYFT_FILE_CONTENT_SKIP_FILES_ABOVE_SIZE"] = "100000000"  # 100MB
        os.environ["SYFT_GOLANG_SEARCH_LOCAL_MOD_CACHE_LICENSES"] = "true"
        os.environ["SYFT_GOLANG_SEARCH_REMOTE_LICENSES"] = "true"
        os.environ["SYFT_LOG_STRUCTURED"] = "true"
        os.environ["SYFT_LOG_LEVEL"] = "info"

    def determine_output_file(  # pylint: disable=too-many-positional-arguments, too-many-arguments
        self, target, scanner_args, inputs, output_dir, file_extension
    ):
        """
        ## Centralized logic to determine output filename.
        ### Args:
            target (str): The target to scan.
            scanner_args (dict): Arguments for the scanner.
            inputs (dict): Inputs from the Github action.
            output_dir (str): The output directory.
            file_extension (str): The file extension for the output file.
        ### Returns:
            str: The determined output file path.
        """

        # 1. First priority: explicitly set output_file in inputs
        if inputs.get("output_file"):
            output_file = inputs.get("output_file")
            # If it's already an absolute path, use it directly
            if os.path.isabs(output_file):
                return output_file
            # Otherwise, join with output_dir
            return os.path.join(output_dir, output_file)

        # 2. Second priority: name and version if available
        name = scanner_args.get("name")
        version = scanner_args.get("version")

        if name:
            if version:
                return f"{output_dir}/{name}_{version}_sbom.{file_extension}"
            return f"{output_dir}/{name}_sbom.{file_extension}"

        # 3. Third priority: image metadata if available
        target_metadata = scanner_args.get("target_metadata", {})
        if "image_name" in target_metadata:
            image_name = target_metadata["image_name"]
            image_version = target_metadata.get("image_version", "latest")
            return f"{output_dir}/{image_name}_{image_version}_sbom.{file_extension}"

        # 4. Final fallback: derive from target path
        target_basename = os.path.basename(target)
        target_name = os.path.splitext(target_basename)[0]
        return f"{output_dir}/{target_name}_sbom.{file_extension}"

    def scan(self, target, scanner_args):
        """
        ## Run Syft scan on the target.
        ### Args:
            target (str): The target to scan.
            scanner_args (dict): Arguments for the scanner.
        ### Returns:
            dict: Dictionary with scan result
        """
        # Configure Syft environment
        self.configure_syft()

        # Get the inputs from the Github action
        inputs = get_inputs()

        # Get format information
        output_dir = inputs.get("output_dir") or "/tmp/sbom"
        logging.info("Output directory: %s", output_dir)
        output_format = inputs.get("output_format")
        if not output_format:
            logging.warning(
                "Empty output format received, using default: cyclonedx-json"
            )
            output_format = "cyclonedx-json"
        logging.info("Output format: %s", output_format)
        file_extension = get_output_file_extension(output_format)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Determine output file using centralized logic
        output_file = self.determine_output_file(
            target, scanner_args, inputs, output_dir, file_extension
        )

        # Create command
        cmd = ["syft", target]

        # Add source name and version if provided and not None
        if "name" in scanner_args and scanner_args["name"] is not None:
            cmd.extend(["--source-name", scanner_args["name"]])
        if "version" in scanner_args and scanner_args["version"] is not None:
            cmd.extend(["--source-version", scanner_args["version"]])

        # Add output format and file
        cmd.extend(["-o", f"{output_format}={output_file}"])

        # Run the command
        logging.info("Running Syft command: %s", " ".join(cmd))
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {
                "sbom_path": output_file,
                "target": target,
                "success": True,
                "stdout": result.stdout,
            }
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e), "stderr": e.stderr}
