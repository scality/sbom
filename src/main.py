#!/usr/bin/env python3
"""This module is the main core of this github action"""

import os
from lib.detect import detect_target_type
from lib.install import install
from lib.scan import ScanCommand
from lib.iso import extract_iso, image_dir_present
from lib.convert import (
    detect_image_origin,
    convert_image_to_oci,
    check_mediatype,
)
from lib.vuln import generate_vuln_report

# Install base packages
install()

# Set variables
if os.environ.get("FORMAT"):
    if os.environ.get("FORMAT") in [
        "syft-json",
        "cyclonedx-xml",
        "cyclonedx-json",
        "spdx-json",
    ]:
        SBOM_FORMAT = os.environ.get("FORMAT")
    else:
        print("Invalid format. Defaulting to cyclonedx-json.")
        SBOM_FORMAT = "cyclonedx-json"
else:
    SBOM_FORMAT = "cyclonedx-json"
print(f"Output format: {SBOM_FORMAT}")

if os.environ.get("OUTPUT_DIR"):
    OUTPUT_DIR = os.environ.get("OUTPUT_DIR")
else:
    OUTPUT_DIR = "/tmp/sbom"
print(f"Output directory: {OUTPUT_DIR}")

if os.environ.get("EXCLUDE_MEDIATYPES"):
    excluded_mediatypes = os.environ.get("EXCLUDE_MEDIATYPES", "").split()
else:
    excluded_mediatypes = []
print(f"Excluded mediatypes: {excluded_mediatypes}")

if os.environ.get("NAME"):
    TARGET_NAME = os.environ.get("NAME")
else:
    TARGET_NAME = None
print(f"Provided target name: {TARGET_NAME}")

if os.environ.get("VERSION"):
    TARGET_VERSION = os.environ.get("VERSION")
else:
    TARGET_VERSION = None
print(f"Provided target version: {TARGET_VERSION}")

vuln_report_str = os.environ.get("VULN_REPORT", "false")
VULN_REPORT = vuln_report_str.lower() == "true"

# Detect target type
target = os.environ.get("TARGET")
print(f"Provided target: {target}")
result = detect_target_type(target)

TARGET_TYPE = result["target_type"]
print(f"Detected target type: {TARGET_TYPE}")
TARGET_NAME = result["name"]
print(f"Detected target name: {TARGET_NAME}")
TARGET_VERSION = result["version"]
print(f"Detected target version: {TARGET_VERSION}")

# Run the appropriate scanner
print(f"Running {TARGET_TYPE} scanner...")

if TARGET_TYPE == "git":
    scan_command = ScanCommand(
        target=target,
        target_type="dir",
        name=TARGET_NAME,
        version=TARGET_VERSION,
        output_dir=OUTPUT_DIR,
        output_file_prefix="repo",
        sbom_format=SBOM_FORMAT,
    )
    scan_command.execute()

elif TARGET_TYPE == "directory":
    scan_command = ScanCommand(
        target=target,
        target_type="dir",
        name=TARGET_NAME,
        version=TARGET_VERSION,
        output_dir=OUTPUT_DIR,
        output_file_prefix="dir",
        sbom_format=SBOM_FORMAT,
    )
    scan_command.execute()

elif TARGET_TYPE == "iso":
    extracted_dir = extract_iso(target)
    image_dir = image_dir_present(extracted_dir)
    scan_command = ScanCommand(
        target=extracted_dir,
        target_type="dir",
        name=TARGET_NAME,
        version=TARGET_VERSION,
        output_dir=OUTPUT_DIR,
        output_file_prefix="iso",
        sbom_format=SBOM_FORMAT,
    )
    scan_command.execute()
    if image_dir is None:
        print("Image directory not found.")
    else:
        print("Image directory found, scanning images.")
        OUTPUT_FILE_PREFIX = "image"
        CONVERT_DIR = "/tmp/images"
        for root, dirs, _ in os.walk(image_dir):
            for image_dir in dirs:
                dir_path = os.path.join(root, image_dir)
                image_name = os.path.basename(dir_path)
                if os.path.isdir(dir_path):
                    for subroot, subdirs, _ in os.walk(dir_path):
                        for subdir in subdirs:
                            # show version of the image
                            image_version = os.path.basename(subdir)
                            print(f"Detected image name: {image_name}")
                            print(f"Detected image version: {image_version}")
                            subdir_path = os.path.join(subroot, subdir)
                            print(f"Scanning image dir: {subdir_path}")
                            detect_image_origin(subdir_path)
                            EXCLUDED = check_mediatype(
                                subdir_path, excluded_mediatypes
                            )
                            if not EXCLUDED:
                                convert_image_to_oci(
                                    subdir_path,
                                    f"{CONVERT_DIR}/{image_name}_{image_version}",
                                )
                                scan_command = ScanCommand(
                                    target=f"{CONVERT_DIR}/{image_name}_{image_version}",
                                    target_type="oci-dir",
                                    name=image_name,
                                    version=image_version,
                                    output_dir=OUTPUT_DIR,
                                    output_file_prefix=OUTPUT_FILE_PREFIX,
                                    sbom_format=SBOM_FORMAT,
                                )
                                scan_command.execute()
                            else:
                                print(f"Excluded image: {subdir_path}")
                                scan_command = ScanCommand(
                                    target=f"{subdir_path}",
                                    target_type="dir",
                                    name=image_name,
                                    version=image_version,
                                    output_dir=OUTPUT_DIR,
                                    output_file_prefix=OUTPUT_FILE_PREFIX,
                                    sbom_format=SBOM_FORMAT,
                                )
                                scan_command.execute()

if VULN_REPORT:
    generate_vuln_report(OUTPUT_DIR)
