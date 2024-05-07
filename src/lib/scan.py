"""Module providing scan command generation"""
import os
import subprocess

class ScanCommand:
    """
    ## This class represents the scan command.
    """

    def __init__(
            self,
            target=None,
            target_type=None,
            name=None,
            version=None,
            output_dir=None,
            output_file_prefix=None,
            sbom_format=None
            ):
        self.target = target
        self.target_type = target_type
        self.name = name
        self.version = version
        self.output_dir = output_dir
        self.sbom_format = sbom_format
        self.output_file_prefix = output_file_prefix
        self.output_file = (
            f"{self.sbom_format}={self.output_dir}/"
            f"{self.output_file_prefix}_{self.name.replace(':', '_')}_{self.version}.json"
        )

    def execute(self):
        """
        ## This function executes the scan command.
        """
        # Ensure output_dir exists
        if self.output_dir is not None:
            os.makedirs(self.output_dir, exist_ok=True)

        # Start with the base command
        command = ["syft", "scan"]

        # Add the target if it's not None
        if self.target is None:
            print("Target is required")
            exit(1)
        if self.target_type is not None:
            command.append(f"{self.target_type}:{self.target}")
        else:
            command.append(self.target)

        # Add the name if it's not None
        if self.name is not None:
            command.append("--source-name")
            command.append(self.name)

        # Add the version if it's not None
        if self.version is not None:
            command.append("--source-version")
            command.append(self.version)

        # Set output_file here, after all necessary attributes have been set
        command.append("--output")
        command.append(self.output_file)

        print(command)
        subprocess.run(
            command,check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
            )
