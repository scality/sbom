#!/usr/bin/env python3
""""
Update scanner versions in the install.py file.
This script fetches the latest release versions of the specified scanners
from their GitHub repositories and updates the version strings in the
install.py file while preserving the original file format.
"""

import os
import sys
import re
import requests

# Add the root directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, root_dir)

# Now we can import from src
from src.modules.install import PACKAGES  # pylint: disable=wrong-import-position


def get_latest_release(package_name, package_info):
    """Fetch the latest release version from a GitHub repository."""
    editor = package_info["editor"]
    url = f"https://api.github.com/repos/{editor}/{package_name}/releases/latest"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()["tag_name"].lstrip("v")
    except Exception as e:
        print(f"⚠ Error fetching latest version for {package_name}: {str(e)}")
        return None


def update_versions(file_path):
    """Update the tools versions in the specified file while preserving format."""
    # Read the file content
    with open(file_path, "r", encoding="utf8") as file:
        content = file.read()

    original_content = content
    updates_made = False

    # First pass: collect update information and modify content
    for package_name, package_info in PACKAGES.items():
        current_version = package_info["default_version"]

        # Get latest version from GitHub
        latest_version = get_latest_release(package_name, package_info)

        if not latest_version:
            continue

        if current_version != latest_version:
            print(f"⬆ Updating {package_name} from {current_version} to {latest_version}")

            # This is a more specific pattern that ensures we're only replacing
            # within the right package section
            pattern = rf'("{package_name}":\s*{{\s*"default_version":\s*")[0-9]+\.[0-9]+\.[0-9]+'

            # Use a replacement function instead of an f-string with backreferences
            def replacement(match):
                return match.group(1) + latest_version

            # Apply the substitution
            new_content = re.sub(pattern, replacement, content)

            # Check if substitution was successful
            if new_content != content:
                content = new_content
                updates_made = True
            else:
                print(f"⚠ Failed to update {package_name} version in the file")
        else:
            print(f"✓ {package_name} is already at latest version {latest_version}")

    # If no updates or no changes made, return early
    if not updates_made:
        print("✓ All tools are already at their latest versions. No updates needed.")
        return

    # Verify changes were actually made
    if content == original_content:
        print("⚠ No changes were made to the file despite updates being found.")
        return

    # Write the updated content back to the file
    with open(file_path, "w", encoding="utf8") as file:
        file.write(content)
    print("✓ Updates applied to", file_path)


if __name__ == "__main__":
    update_versions(os.path.join(root_dir, "src", "modules", "install.py"))
