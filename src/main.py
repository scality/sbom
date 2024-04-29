import os
from lib.detect import detect_target_type
from lib.install import install
from lib.scan import ScanCommand
from lib.iso import extract_iso, image_dir_present
from lib.convert import detect_image_origin, convert_image_to_oci, get_mediatype
from lib.vuln import generate_vuln_report

# Install base packages
install()

# Set default values
format = os.environ.get("FORMAT")
if format is None:
    format = "cyclonedx-json"

version = os.environ.get("VERSION")
print(f"Version: {version}")

output_dir = os.environ.get("OUTPUT_DIR")
if output_dir is None:
    output_dir = "/tmp/sbom"
print(f"Output directory: {output_dir}")

excluded_mediatypes = os.environ.get("EXCLUDE_MEDIATYPES")

vuln_report = os.environ.get("VULN_REPORT")

# Detect target type
target = os.environ.get("TARGET")
print(f"Target: {target}")
result = detect_target_type(target)

target_type = result["target_type"]
name = result["name"]
version = result["version"]

# Run the appropriate scanner
print(f"Running {target_type} scanner...")

if target_type == "git":
    target_type = "dir"
    scan_command = ScanCommand(target=target, target_type=target_type, name=name, version=version, output_dir=output_dir, output_file_prefix="repo", format=format)
    scan_command.execute()

if target_type == "directory":
    target_type = "dir"
    scan_command = ScanCommand(target=target, target_type=target_type, name=name, version=version, output_dir=output_dir, output_file_prefix="dir", format=format)
    scan_command.execute()

if target_type == "iso":
    extracted_dir = extract_iso(target)
    image_dir = image_dir_present(extracted_dir)
    target_type = "dir"
    if image_dir is None:
        print("Image directory not found.")
        scan_command = ScanCommand(target=extracted_dir, target_type=target_type, name=name, version=version, output_dir=output_dir, output_file_prefix="iso", format=format)
        scan_command.execute()
    else:
        output_file_prefix = "image"
        convert_dir = "/tmp/images"
        for root, dirs, _ in os.walk(image_dir):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                image_name = os.path.basename(dir_path)
                if os.path.isdir(dir_path):
                    for subroot, subdirs, _ in os.walk(dir_path):
                        for subdir in subdirs:
                            # show version of the image
                            image_version = os.path.basename(subdir)
                            print(f"Image name: {image_name}")
                            print(f"Image version: {image_version}")
                            subdir_path = os.path.join(subroot, subdir)
                            print(f"Scanning image: {subdir_path}")
                            detect_image_origin(subdir_path)
                            excluded = get_mediatype(subdir_path, excluded_mediatypes)
                            if not excluded:
                                convert_image_to_oci(subdir_path, f"{convert_dir}/{image_name}_{image_version}")
                                scan_command = ScanCommand(target=f"{convert_dir}/{image_name}_{image_version}", target_type="oci-dir", name=image_name, version=image_version, output_dir=output_dir, output_file_prefix=image_name, format=format)
                                scan_command.execute()
                            if excluded:
                                print(f"Excluded image: {subdir_path}")
                                scan_command = ScanCommand(target=f"{subdir_path}", target_type="dir", name=image_name, version=image_version, output_dir=output_dir, output_file_prefix=image_name, format=format)
                                scan_command.execute()

if vuln_report:
    print("Generating vulnerability report...")
    generate_vuln_report(output_dir)
