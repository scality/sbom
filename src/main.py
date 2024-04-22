import os
import argparse
import subprocess
from urllib.parse import urlparse

# if workdir is set in env, use it
work_dir = os.getenv("work_dir", "/tmp/sbom")

parser = argparse.ArgumentParser(
                        prog="sbom-gen",
                        description="SBOM Generation Tool")
parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
subparsers = parser.add_subparsers(help="sub-command help", dest="subparser_name")

parser_install = subparsers.add_parser("install", help="install help")
parser_install.add_argument("-p", "--package", help="package to install")
parser_install.add_argument("-v", "--version", help="version to install")

parser_download = subparsers.add_parser("download", help="download help")
parser_download.add_argument("-u", "--username", help="username for authentication", required=False, default=None)
parser_download.add_argument("-p", "--password", help="password for authentication", required=False, default=None)
parser_download.add_argument("-U", "--url", help="URL to download", nargs='+')
parser_download.add_argument("-d", "--output-dir", default=f"{ work_dir }/artifacts", help="output directory")
parser_download.add_argument("-o", "--output-file", help="output file")

parser_scan = subparsers.add_parser("scan", help="scan help")
scan_target_group = parser_scan.add_argument_group("Scan targets", "Choose only one target type to scan")
scan_target_exclusive_group = scan_target_group.add_mutually_exclusive_group(required=True)
scan_target_exclusive_group.add_argument("-f", "--file", help="file to scan")
scan_target_exclusive_group.add_argument("-p", "--path", help="path to scan")
scan_target_exclusive_group.add_argument("-i", "--image", help="image to scan")
scan_target_exclusive_group.add_argument("-I", "--iso", help="ISO to scan")
parser_scan.add_argument("-e", "--exclude_mediatypes", nargs='+', help="Media types to ignore")
parser_scan.add_argument("-o", "--output-dir", default=f"{ work_dir }/results", help="directory to store scan results")
parser_scan.add_argument("-r", "--report", action='store_true', help="Generate vlnerability report in a file")
parser_scan.add_argument("-F", "--format", default="cyclonedx-json", help="format of the SBOM, default is cyclonedx-json. Choose one of: spdx, spdx-json, cyclonedx, cyclonedx-json")

args = parser.parse_args()
config = vars(args)

if args.subparser_name == "download":
    urls = config["url"]
    username = config["username"] if config["username"] else ""
    password = config["password"] if config["password"] else ""
    output_file = config["output_file"] if config["output_file"] else None
    output_dir = config["output_dir"] if config["output_dir"] else None
    
    for url in urls:
        if output_file is None:
            output_file = os.path.basename(urlparse(url).path)
        
        subprocess.run(["python3", "src/download.py", url, username, password, output_dir, output_file])
        output_file = None  # Reset output_file for the next iteration

if args.subparser_name == "install":
    package = config["package"] if config["package"] else "all"
    version = config["version"] if config["version"] else None
    command = ["python3", "src/install.py", package]
    if version:
        command.append(version)
    subprocess.run(command)

if args.subparser_name == "scan":
    command = ["python3", "src/scan.py"]
    
    if config["file"]:
        command.extend(["--file", config["file"]])
    if config["path"]:
        command.extend(["--path", config["path"]])
    if config["image"]:
        command.extend(["--image", config["image"]])
    if config["iso"]:
        command.extend(["--iso", config["iso"]])
    if config["format"]:
        command.extend(["--format", config["format"]])
    if config["output_dir"]:
        command.extend(["--output-dir", config["output_dir"]])
    if config["exclude_mediatypes"]:
        command.append("--exclude_mediatypes")
        command.extend(config["exclude_mediatypes"])
    if config["report"]:
        command.append("--report")

    print(command)
    subprocess.run(command)