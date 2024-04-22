import argparse
import subprocess
import versions

anchore_base_url = "https://github.com/anchore/{package_name}/releases/download/v{version}/{package_name}_{version}_linux_amd64.tar.gz"
aquasec_base_url = "https://github.com/aquasecurity/{package_name}/releases/download/v{version}/{package_name}_{version}_Linux-64bit.tar.gz"

def install_package(package_name, version):
    print(f"Checking if {package_name} version {version} is already installed...")
    try:
        result = subprocess.run([package_name, "--version"], capture_output=True, text=True)
        print("Installed version: ", result.stdout)
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
    subprocess.run(["sudo", "wget", f"{base_url.format(package_name=package_name, version=version)}", "-O", f"{package_name}_v{version}.tar.gz"])
    subprocess.run(["sudo", "mkdir", f"tmp_{package_name}"])
    subprocess.run(["sudo", "tar", "xvf", f"{package_name}_v{version}.tar.gz", "-C", f"tmp_{package_name}"])
    subprocess.run(["sudo", "mv", f"tmp_{package_name}/{package_name}", "/usr/local/bin/"])
    subprocess.run(["sudo", "rm", "-rf", f"tmp_{package_name}", f"{package_name}_v{version}.tar.gz"])
    print(f"{package_name} version {version} installed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("package_name")
    parser.add_argument("version", nargs='?', default=None)
    args = parser.parse_args()

    #load the versions from versions.py if not provided
    if args.version is None:
        version = versions.scanners.get(args.package_name)
    else:
        version = args.version

    # install all if name is not provided
    if args.package_name == "all":
        for package_name in ["syft", "grype", "trivy"]:
            version = versions.scanners.get(package_name)
            install_package(package_name, version)
        exit(0)
    elif args.package_name in versions.scanners:
        install_package(args.package_name, version)

