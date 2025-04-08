"""Grype scanner implementation."""

import os
import subprocess
import logging
from config.inputs import get_inputs, FORMAT_EXTENSIONS
from config.outputs import create_standard_result


class GrypeScanner:
    """Scanner implementation for Grype."""

    BASE_TEMPLATE_PATH = os.getenv("GITHUB_ACTION_PATH", os.getcwd())
    # Map format types to appropriate file extensions
    TEMPLATES_PATH = {
        "csv": os.path.join(BASE_TEMPLATE_PATH, "src/config/templates/csv.tmpl"),
        "html": os.path.join(BASE_TEMPLATE_PATH, "src/config/templates/html.tmpl"),
        "junit": os.path.join(BASE_TEMPLATE_PATH, "src/config/templates/junit.tmpl"),
        "table": os.path.join(BASE_TEMPLATE_PATH, "src/config/templates/table.tmpl"),
    }

    def configure_grype(self):
        """
        ## Configure Grype environment variables.
        ### This method sets the environment variables required for Grype to run.
        """
        os.environ["GRYPE_SEARCH_SCOPE"] = "all-layers"
        os.environ["GRYPE_LOG_LEVEL"] = "info"
        os.environ["GRYPE_PRETTY"] = "true"

    def determine_output_file(  # pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-return-statements
        self, target, scanner_args, inputs, output_dir, file_extension
    ):
        """
        ## Centralized logic to determine vulnerability output filename.
        ### Args:
            target (str): The target to scan.
            scanner_args (dict): Arguments for the scanner.
            inputs (dict): Inputs from the Github action.
            output_dir (str): The output directory.
            file_extension (str): The file extension for the output file.
        ### Returns:
            str: The determined output file path.
        ### Notes:
            Uses the same priority as Syft scanner for consistency:
            1. Explicitly set vuln_output_file in inputs
            2. Name and version if available
            3. Image metadata if available
            4. Derive from target path
        """
        # 1. First priority: explicitly set vuln_output_file in inputs
        if inputs.get("vuln_output_file"):
            vuln_output_file = inputs.get("vuln_output_file")
            # If it's already an absolute path, use it directly
            if os.path.isabs(vuln_output_file):
                return vuln_output_file
            # Otherwise, join with output_dir
            return os.path.join(output_dir, vuln_output_file)

        # 2. Second priority: name and version if available
        name = scanner_args.get("name")
        version = scanner_args.get("version")

        if name:
            if version:
                return f"{output_dir}/{name}_{version}_vuln.{file_extension}"
            return f"{output_dir}/{name}_vuln.{file_extension}"

        # 3. Third priority: image metadata if available
        target_metadata = scanner_args.get("target_metadata", {})
        if "image_name" in target_metadata:
            image_name = target_metadata["image_name"]
            image_version = target_metadata.get("image_version", "latest")
            return f"{output_dir}/{image_name}_{image_version}_vuln.{file_extension}"

        # 4. Final fallback: derive from target path
        # First, use the SBOM file path as a base if it's a vuln scan of an SBOM
        if os.path.exists(target) and (
            target.endswith(".json")
            or target.endswith(".xml")
            or target.endswith(".spdx")
        ):
            target_basename = os.path.basename(target)
            target_name = os.path.splitext(target_basename)[0]
            return f"{output_dir}/{target_name}_vuln.{file_extension}"

        # Otherwise use the target directory/file
        target_basename = os.path.basename(target)
        target_name = os.path.splitext(target_basename)[0]
        return f"{output_dir}/{target_name}_vuln.{file_extension}"

    def scan(self, target, scanner_args):
        """
        ## Run Grype scan on the target.
        ### Args:
            target (str): The target to scan.
            scanner_args (dict): Arguments for the scanner.
        ### Returns:
            dict: The result of the scan.
        """
        # Configure Grype environment
        self.configure_grype()

        # Get the inputs from the Github action
        inputs = get_inputs()

        # Get output directory
        output_dir = inputs.get("output_dir") or "/tmp/sbom"

        # Initialize vuln_output_format properly
        vuln_output_format = inputs.get("vuln_output_format") or inputs.get(
            "output_format", "cyclonedx-json"
        )

        logging.info("Vulnerability output format: %s", vuln_output_format)

        # Convert string to list if needed
        if isinstance(vuln_output_format, str):
            # Handle comma-separated formats
            if "," in vuln_output_format:
                formats = [f.strip() for f in vuln_output_format.split(",")]
            else:
                formats = [vuln_output_format]
        else:
            formats = ["json"]  # Default format

        logging.info("Output formats: %s", formats)

        results = {"success": True, "reports": {}}
        paths = {}

        for report_format in formats:
            file_extension = FORMAT_EXTENSIONS.get(report_format, "json")
            logging.info("File extension: %s", file_extension)

            # Use the new determine_output_file method
            output_file = self.determine_output_file(
                target, scanner_args, inputs, output_dir, file_extension
            )

            # Run scan for each report format
            report_result = self._run_scan(
                target, report_format, output_file, scanner_args
            )
            results["reports"][report_format] = report_result

            if report_result.get("success", False):
                paths[report_format] = report_result.get("vuln_path")

        # Build a standardized and flat output
        return create_standard_result(
            scanner="syft",
            success=results.get("success", False),
            target=target,
            name=scanner_args.get("name"),
            version=scanner_args.get("version"),
            sbom_path=output_file if results.get("success") else None,
            stdout=results.get("stdout"),
            error=results.get("error"),
            additional={"report": results},
        )

    def _run_scan(self, target, report_format, output_file, scanner_args):
        """
        ## Run the Grype scan.
        ### Args:
            target (str): The target to scan.
            report_format (str): The format of the report.
            output_file (str): The output file path.
            scanner_args (dict): Additional arguments for the scanner.
        ### Returns:
            dict: The result of the scan.
        """
        # Create command
        cmd = ["grype", target]

        # Add distro info if available
        distro = scanner_args.get("distro")
        distro_version = scanner_args.get("distro_version")
        if distro and distro_version:
            cmd.extend(["--distro", f"{distro}:{distro_version}"])

        # Add name if available
        name = scanner_args.get("name")
        if name:
            cmd.extend(["--name", name])

        # Handle template formats
        if report_format in self.TEMPLATES_PATH:
            template_path = self.TEMPLATES_PATH[report_format]
            if not os.path.exists(template_path):
                logging.error("Template file not found: %s", template_path)
                return {
                    "format": report_format,
                    "success": False,
                    "error": f"Template file not found: {template_path}",
                }
            cmd.extend(["--template", template_path])
            cmd.extend(["-o", "template"])
            cmd.extend(["--file", output_file])
        # Handle custom template provided as input
        elif report_format == "template" and "template_file" in scanner_args:
            cmd.extend(["--template", scanner_args["template_file"]])
            cmd.extend(["-o", "template"])
            cmd.extend(["--file", output_file])
        # Standard formats
        else:
            cmd.extend(["-o", report_format])
            cmd.extend(["--file", output_file])

        # Add CPEs if none
        cmd.append("--add-cpes-if-none")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Run the command
        logging.info("Running Grype command: %s", " ".join(cmd))

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {
                "vuln_path": output_file,
                "format": report_format,
                "success": True,
                "stdout": result.stdout,
            }
        except subprocess.CalledProcessError as e:
            return {
                "format": report_format,
                "success": False,
                "error": str(e),
                "stderr": e.stderr,
            }
