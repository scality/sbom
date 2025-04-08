"""Module providing installation of required tools for the project."""

import logging
import os
import hashlib
import tempfile
import subprocess
import shutil
import yaml
import requests
from pyunpack import Archive


# Load package information from versions.yaml
def load_packages():
    """Load package configurations from versions.yaml file."""
    yaml_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "versions.yaml"
    )
    try:
        with open(yaml_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        packages = data.get("packages", {})
        return packages
    except Exception as e:
        logging.error("Failed to load versions.yaml: %s", str(e))
        raise


PACKAGES = load_packages()
BASE_URL = "https://github.com/{editor}/{name}/releases/download/v{version}/"
CHECKSUMS = "{package_name}_{version}_checksums.txt"
INSTALL_DIR = "/usr/local/bin"


def get_package_info(package_name):
    """
    ## Get package information dictionary for a given package.
    ### Args:
        package_name (str): Name of the package
    ### Returns:
        dict: Package information (default_version, editor, artifact) or None if not found
    """
    return PACKAGES.get(package_name)


def set_versions(tool_versions, package_name):
    """
    ## Set the package version.
    Uses tool_versions from the GitHub Action inputs if provided, otherwise falls back
    to the default version in PACKAGES.
    ### Args:
        tool_versions (dict): Dictionary of tool versions
        package_name (str): Name of the package
    ### Returns:
        str: Version of the package
    """
    info = get_package_info(package_name)
    if not info:
        raise ValueError(f"Package info not available for: {package_name}")

    version = tool_versions.get(f"{package_name}_version")
    if version:
        logging.info(
            "Using version %s for %s from tool versions.", version, package_name
        )
        return version

    default_version = info["default_version"]
    logging.info("Using default version %s for %s.", default_version, package_name)
    return default_version


def get_checksum(checksums_url, package_name, version, artifact_file):
    """
    ## Get the expected checksum for a package from the checksums file.
    ### Args:
        checksums_url (str): URL for the checksums file
        package_name (str): Name of the package
        version (str): Version of the package
        artifact_file (str): Name of the artifact file
    ### Returns:
        str: Expected checksum or None if not found
    """
    info = get_package_info(package_name)
    if not info:
        return None

    checksums_enabled = info.get("checksums", False)
    if not checksums_enabled:
        logging.warning("Checksum verification is disabled for %s", package_name)
        return None

    checksums_filename = checksums_url.format(
        package_name=package_name, version=version
    )
    url = (
        BASE_URL.format(editor=info["editor"], name=package_name, version=version)
        + checksums_filename
    )
    logging.info("Downloading checksums from %s", url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.warning("Error downloading checksums: %s", str(e))
        logging.warning("Continuing without checksum verification")
        return None

    for line in response.text.splitlines():
        if artifact_file in line:
            return line.split()[0]

    logging.warning("Could not find checksum for %s in checksums file", artifact_file)
    logging.warning("Continuing without checksum verification")
    return None


def check_permissions():
    """
    ## This function checks the permissions of the user.
    ### Returns:
        bool: True if the user has root permissions, False otherwise
    """
    return os.geteuid() == 0


def check_package_version(package_name, version):
    """
    ## This function checks if the package and version are already installed.
    ### Args:
        package_name (str): Name of the package
        version (str): Version of the package
    ### Returns:
        bool: True if the package is installed, False otherwise
    """
    logging.info(
        "Checking if %s version %s is already installed...", package_name, version
    )
    try:
        result = subprocess.check_output([package_name, "--version"], text=True)
        if version in result:
            logging.info("%s version %s is already installed.", package_name, version)
            return True
    except FileNotFoundError:
        logging.warning("Package %s is not installed.", package_name)

    logging.info("Installing %s version %s", package_name, version)
    return False


def verify_checksum(file_path, expected_checksum):
    """
    ## Verify the checksum of a downloaded file.
    ### Args:
        file_path (str): Path to the downloaded file
        expected_checksum (str): Expected SHA256 checksum
    ### Returns:
        bool: True if checksum matches, raises ValueError otherwise
    """
    if not expected_checksum:
        logging.warning("No checksum available for verification, skipping")
        return True

    logging.info("Verifying checksum of %s", file_path)
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    calculated_checksum = sha256_hash.hexdigest()

    if calculated_checksum != expected_checksum:
        raise ValueError(
            f"Checksum verification failed!\n"
            f"Expected: {expected_checksum}\n"
            f"Got: {calculated_checksum}"
        )

    logging.info("Checksum verified successfully.")
    return True


def download_file(url, output_path, package_name=None, version=None):
    """
    ## Download a file from a URL with progress reporting and optional checksum verification.
    ### Args:
        url (str): URL to download from
        output_path (str): Path to save the file
        package_name (str, optional): Name of the package (for checksum verification)
        version (str, optional): Version of the package (for checksum verification)
    ### Returns:
        str: Path to the downloaded file
    """
    logging.info("Downloading %s to %s", url, output_path)

    # Create parent directories if they don't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    response = requests.get(url, stream=True, timeout=10)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(
            f"Failed to download file. HTTP status code: {response.status_code}"
        )

    # Get total size for progress reporting if available
    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            # Simple progress reporting
            if total_size > 0:
                percent = int(100 * downloaded / total_size)
                print(
                    f"\rProgress: {percent}% ({downloaded}/{total_size} bytes)",
                    end="",
                )

    if total_size > 0:
        print()  # New line after progress

    logging.info("Downloaded complete: %s", output_path)

    # Verify checksum if requested and package info provided
    verify_enabled = PACKAGES.get(package_name, {}).get("checksums", False)

    if verify_enabled and package_name and version:
        artifact_pattern = PACKAGES.get(package_name)["artifact"]
        if "{" in artifact_pattern:
            artifact_file = artifact_pattern.format(
                package_name=package_name, version=version
            )
        else:
            artifact_file = artifact_pattern

        expected_checksum = get_checksum(
            CHECKSUMS, package_name, version, artifact_file
        )
        verify_checksum(output_path, expected_checksum)

    return output_path


def install_package(package_name, version):
    """
    ## Install the specified package and version using temporary files and checksum verification.
    ### Args:
        package_name (str): Name of the package to install
        version (str): Version of the package to install
    """
    editor = PACKAGES[package_name]["editor"]
    artifact_name = PACKAGES[package_name]["artifact"].format(
        package_name=package_name, version=version
    )

    download_url = (
        BASE_URL.format(editor=editor, name=package_name, version=version)
        + artifact_name
    )

    # Create a temporary directory that will be automatically cleaned up
    with tempfile.TemporaryDirectory(prefix=f"{package_name}_") as temp_dir:
        download_path = os.path.join(temp_dir, artifact_name)

        # Download with progress reporting and checksum verification
        download_file(download_url, download_path, package_name, version)

        # Extract the archive if it's a compressed file
        if artifact_name.endswith(".tar.gz"):
            logging.info("Extracting %s...", artifact_name)
            try:
                Archive(download_path).extractall(temp_dir)
            except ValueError as error:
                logging.error(
                    "Error extracting archive %s: %s", artifact_name, str(error)
                )

        binary_name = PACKAGES[package_name]["binary"]
        binary_path = os.path.join(temp_dir, binary_name)
        if not os.path.exists(binary_path):
            # Try to find the binary if it's not directly in the temp directory
            for root, _, files in os.walk(temp_dir):
                if binary_name in files:
                    binary_path = os.path.join(root, binary_name)
                    break

            if not os.path.exists(binary_path):
                raise FileNotFoundError(
                    f"Could not find {binary_name} binary in extracted files"
                )

        # Make the binary executable
        os.chmod(binary_path, 0o755)

        # Install the binary
        install_path = os.path.join(INSTALL_DIR, package_name)
        logging.info("Installing %s to %s...", package_name, install_path)

        if not check_permissions():
            # Use sudo to copy the file
            subprocess.run(["sudo", "cp", binary_path, install_path], check=True)
        else:
            # Direct copy if we have permissions
            shutil.copy(binary_path, install_path)

        logging.info("%s version %s installed successfully.", package_name, version)


def install_tool(tool_versions):
    """
    ## This function installs the base packages.
    ### Args:
        tool_versions (dict): Dictionary of tool versions
    """
    for package_name in PACKAGES:
        version = set_versions(tool_versions, package_name)
        if not check_package_version(package_name, version):
            install_package(package_name, version)
