#!/usr/bin/env python3
""""
Update scanner versions in the install.py file.
This script fetches the latest release versions of the specified scanners
from their GitHub repositories and updates the version strings in the
install.py file.
"""

import re
import requests

# Define the scanners and their GitHub repositories
SCANNERS = {
    "syft": "anchore/syft",
    "grype": "anchore/grype",
}

def get_latest_release(repo):
    """Fetch the latest release version from a GitHub repository."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()["tag_name"].lstrip("v")

def update_versions(file_path):
    """Update the scanner versions in the specified file."""
    content = None
    with open(file_path, "r", encoding="utf8") as file:
        content = file.read()

        # Find the scanners dictionary block
        scanners_pattern = r"SCANNERS = \{(.*?)\}"
        scanners_match = re.search(scanners_pattern, content, re.DOTALL)

    if not scanners_match:
        raise ValueError("Could not find scanners dictionary in the file")

    scanners_block = scanners_match.group(0)
    updated_block = scanners_block
    updates_made = False

    for scanner, repo in SCANNERS.items():
        # Extract current version from the file
        current_version_pattern = rf'"{scanner}": "([0-9]+\.[0-9]+\.[0-9]+)"'
        current_version_match = re.search(current_version_pattern, scanners_block)
        current_version = current_version_match.group(1) if current_version_match else "unknown"

        # Get latest version from GitHub
        latest_version = get_latest_release(repo)

        # Compare versions
        if current_version == latest_version:
            print(f"✓ {scanner} is already at latest version {latest_version}")
            continue

        # Version is different, update needed
        print(f"⬆ Updating {scanner} from {current_version} to {latest_version}")
        updates_made = True

        # Build pattern and replacement
        scanner_pattern = rf'("{scanner}": ")([0-9]+\.[0-9]+\.[0-9]+)'

        # Use lambda for replacement
        updated_block = re.sub(
            scanner_pattern,
            lambda match, version=latest_version: match.group(1) + version, updated_block)

    # If no updates were made, print and return
    if not updates_made:
        print("✓ All scanners are already at their latest versions. No updates needed.")
        return

    # Write to file if changes were made
    content = content.replace(scanners_block, updated_block)
    with open(file_path, "w", encoding="utf8") as file:
        file.write(content)
    print("✓ Updates applied to", file_path)

if __name__ == "__main__":
    update_versions("src/modules/install.py")
