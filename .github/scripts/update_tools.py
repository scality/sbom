#!/usr/bin/env python3
""""
Update scanner versions in the versions.yaml file.
This script fetches the latest release versions of the specified scanners
from their GitHub repositories and updates the version strings in the
versions.yaml file while preserving the original file format.
"""

from pathlib import Path
import os
import sys
import yaml
import requests

# Add the root directory to the Python path
root_dir = Path(__file__).resolve().parents[2]

def load_packages():
    """Load package configurations from versions.yaml file."""
    yaml_path = os.path.join(root_dir, "versions.yaml")
    try:
        with open(yaml_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        # Expect data["packages"] to be a dict
        packages = data.get("packages", {})
        data["packages"] = packages
        return data
    except yaml.YAMLError as error:
        print(f"⚠ Error loading versions.yaml: {str(error)}")
        raise

def get_latest_release(package_name, package_info):
    """Fetch the latest release version from a GitHub repository."""
    editor = package_info["editor"]
    url = f"https://api.github.com/repos/{editor}/{package_name}/releases/latest"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()["tag_name"].lstrip("v")
    except requests.RequestException as error:
        print(f"⚠ Error fetching latest version for {package_name}: {str(error)}")
        return None

def update_versions(file_path):
    """Update the tools versions in the specified file while preserving format."""
    data = load_packages()
    updates_made = False
    packages = data.get("packages", {})

    # Iterate over package dictionary
    for package_name, package in packages.items():
        current_version = package["default_version"]
        latest_version = get_latest_release(package_name, package)
        if not latest_version:
            continue
        if current_version != latest_version:
            print(f"⬆ Updating {package_name} from {current_version} to {latest_version}")
            package["default_version"] = latest_version
            updates_made = True
        else:
            print(f"✓ {package_name} is already at latest version {latest_version}")

    if not updates_made:
        print("✓ All tools are already at their latest versions. No updates needed.")
        return

    # Write the updated data back to the file
    with open(file_path, "w", encoding="utf8") as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=False)
    print("✓ Updates applied to", file_path)

if __name__ == "__main__":
    update_versions(os.path.join(root_dir, "versions.yaml"))
