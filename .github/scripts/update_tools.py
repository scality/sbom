#!/usr/bin/env python3
""""
Update scanner versions in the versions.yaml file.
This script fetches the latest release versions of the specified scanners
from their GitHub repositories and updates the version strings in the
versions.yaml file while preserving the original file format.
"""

from pathlib import Path
import yaml
import requests

# Add the root directory to the Python path
ROOT_DIR = Path(__file__).resolve().parents[2]
VERSION_FILE = ROOT_DIR / "versions.yaml"

def load_packages():
    """Load package configurations from versions.yaml file."""
    try:
        data = yaml.safe_load(VERSION_FILE.read_text(encoding="utf-8"))
        return data
    except (yaml.YAMLError, FileNotFoundError) as error:
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

def update_versions():
    """Update the tools versions in the versions file while preserving format."""
    updates_made = False
    data = load_packages()
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

    # Write the updated data back to the file using the constant VERSION_FILE
    VERSION_FILE.write_text(
        yaml.dump(data, default_flow_style=False, sort_keys=False),
        encoding="utf8"
    )
    print("✓ Updates applied to", VERSION_FILE)

if __name__ == "__main__":
    update_versions()
