import os
import subprocess

class ScanCommand:
    def __init__(
            self,
            target=None,
            target_type=None,
            name=None,
            version=None,
            output_dir=None,
            output_file_prefix=None,
            format=None
            ):
        self.target = target
        self.target_type = target_type
        self.name = name
        self.version = version
        self.output_dir = output_dir
        self.format = format
        self.output_file_prefix = output_file_prefix
        self.output_file = (f"{self.format}={self.output_dir }/{self.output_file_prefix}_{self.name}_{self.version}.json") 

    def execute(self):
        # Ensure output_dir exists
        if self.output_dir is not None:
            os.makedirs(self.output_dir, exist_ok=True)

        # Start with the base command
        command = ["syft", "scan"]    

        # Add the target if it's not None
        if self.target is not None:
            if self.target_type is not None:
                command.append(f"{self.target_type}:{self.target}")
            else: command.append(self.target)
        if self.target is None:
            print("Target is required")
            exit(1)

        # Add the name if it's not None
        if self.name is not None:
            command.append("--source-name")
            command.append(self.name)

        # Add the version if it's not None
        if self.version is not None:
            command.append("--source-version")
            command.append(self.version)

        # Set output_file here, after all necessary attributes have been set
        self.output_file = f"{self.format}={self.output_dir}/{self.output_file_prefix}_{self.name}_{self.version}.json"
        command.append(f"-o {self.output_file}")

        print(command)
        subprocess.run(command)