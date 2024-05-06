"""Module providing installation of required scanners"""

import os
import subprocess
import shutil
import requests
from pyunpack import Archive

# Define the scanners and their versions
scanners = {"syft": "1.2.0", "grype": "0.77.2", "trivy": "0.50.1"}

# Define the base URLs for the scanners
ANCHORE_BASE_URL = (
    "https://github.com/anchore/{package_name}/releases/download/"
    "v{version}/{package_name}_{version}_linux_amd64.tar.gz"
)

AQUASEC_BASE_URL = (
    "https://github.com/aquasecurity/{package_name}/releases/download/"
    "v{version}/{package_name}_{version}_Linux-64bit.tar.gz"
)

def set_versions(package_name):
    """
    ## This function sets the versions of the scanners.
    """
    if os.environ.get(f"{package_name.upper()}_VERSION"):
        version = os.environ.get(f"{package_name.upper()}_VERSION")
    else:
        version = scanners[package_name]
    return version

def install_package(package_name, version):
    """
    ## This function installs the specified package and version.
        Supported packages are: syft, grype, trivy
    ### Args:
        - `package_name (string)`: Name of the package to install
        - `version (string)`: Version of the package to install
    """
    print(f"Checking if {package_name} version {version} is already installed...")
    try:
        result = subprocess.check_output([package_name, "--version"], text=True)
        if version in result:
            print(f"{package_name} version {version} is already installed.")
            return
    except FileNotFoundError:
        print(f"{package_name} is not installed.")
    print(f"Installing {package_name} version {version}...")
    if package_name in ["syft", "grype"]:
        base_url = ANCHORE_BASE_URL
    elif package_name == "trivy":
        base_url = AQUASEC_BASE_URL
    # Download tarball
    url = base_url.format(package_name=package_name, version=version)
    print(f"Downloading {package_name} version {version} from {url}...")
    response = requests.get(url, stream=True, timeout=10)
    if response.status_code == 200:
        with open(f"{package_name}_v{version}.tar.gz", "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    else:
        raise requests.exceptions.HTTPError(
            f"Failed to download file. HTTP status code: {response.status_code}"
        )
    # Create temporary extraction dir
    os.makedirs(f"tmp_{package_name}", exist_ok=True)
    # Extract tarball
    Archive(f"{package_name}_v{version}.tar.gz").extractall(f"tmp_{package_name}")
    # Move binary to "/usr/local/bin/"
    shutil.move(f"tmp_{package_name}/{package_name}", f"/usr/local/bin/{package_name}")
    # Delete temporary files and directories
    shutil.rmtree(f"tmp_{package_name}", ignore_errors=True)
    os.remove(f"{package_name}_v{version}.tar.gz")
    print(f"{package_name} version {version} installed.")

def install():
    """
    ## This function installs the base packages.
    """
    for scanner, version in scanners.items():
        version = set_versions(scanner)
        print(f"Installing {scanner} version {version}...")
        install_package(scanner,version)
