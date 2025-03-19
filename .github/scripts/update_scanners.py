#!/usr/bin/env python3

import re
import requests

# Define the scanners and their GitHub repositories
scanners = {
    "syft": "anchore/syft",
    "grype": "anchore/grype",
    "trivy": "aquasecurity/trivy"
}

def get_latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["tag_name"].lstrip("v")

def update_versions(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    for scanner, repo in scanners.items():
        latest_version = get_latest_release(repo)
        content = re.sub(
            f'("{scanner}": ")([^"]+)',
            lambda match: f'{match.group(1)}{latest_version}',
            content
        )

    with open(file_path, "w") as file:
        file.write(content)

if __name__ == "__main__":
    update_versions("src/lib/install.py")