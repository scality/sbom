import subprocess
import os

# Define the scanners and their versions
scanners = {
    "syft": "1.2.0",
    "grype": "0.77.1",
    "trivy": "0.50.1"
}

# Define the base URLs for the scanners
anchore_base_url = "https://github.com/anchore/{package_name}/releases/download/v{version}/{package_name}_{version}_linux_amd64.tar.gz"
aquasec_base_url = "https://github.com/aquasecurity/{package_name}/releases/download/v{version}/{package_name}_{version}_Linux-64bit.tar.gz"

def set_versions():
    grype_version = os.environ.get("INPUT_GRYPE_VERSION")
    if grype_version is not None:
        scanners["grype"] = grype_version
    syft_version = os.environ.get("INPUT_SYFT_VERSION")
    if syft_version is not None:
        scanners["syft"] = syft_version
    trivy_version = os.environ.get("INPUT_TRIVY_VERSION")
    if trivy_version is not None:
        scanners["trivy"] = trivy_version

set_versions()

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
        result = subprocess.run([package_name, "--version"], capture_output=True, text=True)
        if version in result.stdout:
            print(f"{package_name} version {version} is already installed.")
            return
    except FileNotFoundError:
        print(f"{package_name} is not installed.")
    print(f"Installing {package_name} version {version}...")
    if package_name == "syft" or package_name == "grype":
        base_url=anchore_base_url
    elif package_name == "trivy":
        base_url=aquasec_base_url
    subprocess.run([
        "sudo",
        "wget", f"{base_url.format(package_name=package_name, version=version)}",
        "-O", f"{package_name}_v{version}.tar.gz"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([
        "sudo",
        "mkdir", f"tmp_{package_name}"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([
        "sudo","tar", "xvf", f"{package_name}_v{version}.tar.gz", "-C", f"tmp_{package_name}"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([
        "sudo",
        "mv", f"tmp_{package_name}/{package_name}", "/usr/local/bin/"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([
        "sudo", "rm", "-rf", f"tmp_{package_name}", f"{package_name}_v{version}.tar.gz"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"{package_name} version {version} installed.")

def install():
    """
    ## This function installs the base packages.
    """
    for scanner, version in scanners.items():
        install_package(scanner, version)
