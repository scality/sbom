import argparse
import json
import os
import subprocess
import tarfile
from git import Repo, exc

def is_git_repo(path):
    try:
        _ = Repo(path).git_dir
        return True
    except exc.InvalidGitRepositoryError:
        return False

def get_repo_version(path):
    if is_git_repo(path):
        try:
            version = subprocess.check_output(["git", "-C", path, "describe", "--tags"], text=True).strip()
            return version
        except subprocess.CalledProcessError:
            return None

def get_repo_name(path):
    if is_git_repo(path):
        return os.path.basename(os.path.normpath(path))

def detect_image_origin(path):
    if os.path.isdir(path):
        if os.path.isfile(os.path.join(path, "oci-layout")):
            print(f"{path} is an OCI image.")
            return 'oci'
        elif os.path.isfile(os.path.join(path, "manifest.json")):
            print(f"{path} is a Docker image.")
            return 'docker'
    if path.endswith(".tar"):
        with tarfile.open(path) as tar:
            for member in tar.getmembers():
                if member.name == 'manifest.json':
                    print(f"{path} is a Docker image.")
                    return 'docker'
                elif member.name.startswith('blobs/'):
                    print(f"{path} is an OCI image.")
                    return 'oci'
    return 'unknown'

def convert_image_to_oci(image_dir, output_dir):
    image_basename = os.path.basename(image_dir)
    converted_image_dir = f"/tmp/images/{image_basename}"
    if output_dir is not None:
        converted_image_dir = output_dir
        os.makedirs(converted_image_dir, exist_ok=True)
    if detect_image_origin(image_dir) == 'docker':
        subprocess.run(["skopeo", "copy", f"dir:{image_dir}", f"oci:{converted_image_dir}", "--format", "oci"])
        print(f"Converted {image_dir} to OCI format at: {converted_image_dir}")
        return converted_image_dir
    elif detect_image_origin(image_dir) == 'oci':
        print(f"{image_dir} is already in OCI format.")
    else:
        print(f"{image_dir} is not in a recognized format.")

def extract_iso(iso_path):
    #create temporary directory to extract iso
    iso_basename = os.path.basename(iso_path)
    extracted_dir = f"/tmp/{iso_basename}"
    os.makedirs(extracted_dir, exist_ok=True)
    subprocess.run(["7z", "x", iso_path, f"-o{extracted_dir}"])
    print(f"Extracted ISO to: {extracted_dir}")
    return extracted_dir

def vuln_report(output_dir):
    grype_html_command = ["grype", "-o", "template", "-t", "templates/html-table.tmpl"]
    #loop over the results directory and generate a report
    report_dir = f"{output_dir}/reports"
    print(f"Generating report in: {report_dir}")
    os.makedirs(report_dir, exist_ok=True)
    for file in os.listdir(output_dir):
        print(f"Checking file: {file}")
        if file.endswith(".json"):
            print(f"Generating report for: {file}")
            report_file = os.path.splitext(file)[0]
            print(f"Report file: {report_file}")
            grype_html_command.extend([f"sbom:{output_dir}/{file}", "--file", f"{report_dir}/{report_file}.html"])
            print(f"Running command: {grype_html_command}")
            subprocess.run(grype_html_command, check=True)
            #reset the command for the next iteration
            grype_html_command = ["grype", "-o", "template", "-t", "templates/html-table.tmpl"]

def scan():
    command = ["syft"]
    output_file_prefix = 'undefined'
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="File to scan")
    parser.add_argument("-p", "--path", help="Path to scan")
    parser.add_argument("-i", "--image", help="Image to scan")
    parser.add_argument("-I", "--iso", help="ISO to scan")
    parser.add_argument("-e", "--exclude_mediatypes", default=None, nargs='+', help="Media types to ignore")
    parser.add_argument("-n", "--name", default=None, help="Name of the target")
    parser.add_argument("-v", "--version", help="Version of the target")
    parser.add_argument("-F", "--format", default="cyclonedx-json", help="format of the SBOM, default is cyclonedx-json. Choose one of: spdx, spdx-json, cyclonedx, cyclonedx-json")
    parser.add_argument("-o", "--output-dir", default="/tmp/results", help="Directory to store scan results")
    parser.add_argument("-r", "--report", action='store_true', help="Generate vlnerability report in a file")
    args = parser.parse_args()

    print(f"Excluded mediatypes: {args.exclude_mediatypes}")
    def format_output(command, format, output_file_prefix, name, version):
        print(f"Output format: {format}")
        print(f"Output file prefix: {output_file_prefix}")
        print(f"Name: {name}")
        print(f"Version: {version}")
        command.extend(['--output', f"{format}={args.output_dir }/{output_file_prefix}_{name}_{version}.json"])    

    def run_syft_scan(command):
        print(f"Running command: {command}")
        subprocess.run(command, check=True)

    def get_mediatype(image_dir):
        excluded = False
        if args.exclude_mediatypes is not None:
            excluded_media_types = args.exclude_mediatypes
            inspect_command = f"skopeo inspect dir:{image_dir} --raw"
            print(f"Running command: {inspect_command}")
            result = subprocess.run(inspect_command, capture_output=True, text=True, shell=True)
            data = json.loads(result.stdout)
            media_types = []
            if "config" in data and "mediaType" in data["config"]:
                media_types.append(data["config"]["mediaType"])
            if "layers" in data:
                for layer in data["layers"]:
                    if "mediaType" in layer:
                        media_types.append(layer["mediaType"])
            excluded_types = [media_type for media_type in media_types if media_type in excluded_media_types]
            if excluded_types:
                print(f"Excluded media types found: {excluded_types}")
                print("Excluding image")
                excluded = True
            else:
                print("Keeping image")
                excluded = False
        return excluded

    def scan_images(images_dir):
        output_file_prefix = "image"
        for root, dirs, _ in os.walk(images_dir):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                print(f"Checking directory: {dir_path}")
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
                            if get_mediatype(subdir_path) == False:
                                converted_image_dir = convert_image_to_oci(subdir_path, f"/tmp/images/{image_name}_{image_version}")
                                print(f"Converted image: {converted_image_dir}")
                                scan_command = ['syft', 'scan', f"oci-dir:{converted_image_dir}"]
                                format_output(scan_command, args.format, output_file_prefix, image_name, image_version)
                                run_syft_scan(scan_command)
                            else:
                                print(f"Wrong mediatype, exclude image: {subdir_path}")

    if args.file:
        print(f"Scanning file: {args.file}")
        command.extend(['scan', f"file:{args.file}"])
        if args.name is None:
            args.name = os.path.basename(args.file)
            print(f"Found name: {args.name}")
        command.extend(["--source-name", args.name])
        output_file_prefix = "file"
    
    if args.path:
        print(f"Scanning path: {args.path}")
        command.extend(['scan', f"dir:{args.path}"])
        if is_git_repo(args.path):
            if args.version is None and is_git_repo(args.path):
                args.version = get_repo_version(args.path)
                print(f"Found version: {args.version}")
            if args.name is None:
                args.name = get_repo_name(args.path)
                print(f"Found name: {args.name}")
            output_file_prefix = "repo"
        else:
            if args.name is None:
                print(f"Name not provided, using path as name.")
                args.path = args.path.rstrip('/')
                args.name = os.path.basename(args.path)
                print(f"Name used: {args.name}")
            if args.version is None:
                args.version = "undefined"
                print(f"Version not provided, set to: {args.version}")
            output_file_prefix = "path"
        command.extend(["--source-version", args.version])
        command.extend(["--source-name", args.name])
    
    if args.image:
        print(f"Scanning image: {args.image}")
        if os.path.isdir(args.image):
            args.name = os.path.basename(args.image)
            print(f"Name used: {args.name}")
            print(f"{args.image} is a directory.")
            convert_image_to_oci(args.image)
        elif args.image.endswith(".tar"):
            args.name = os.path.basename(args.image)
            #remove .tar extension
            args.name = os.path.splitext(args.name)[0]
            print(f"Name used: {args.name}")
            if detect_image_origin(args.image) == 'docker':
                command.extend(['scan', f"docker-archive:{args.image}"])
            elif detect_image_origin(args.image) == 'oci':
                command.extend(['scan', f"oci-archive:{args.image}"])
        else:
            print(f"{args.image} is not a directory or a recognized file format.")
        output_file_prefix = "image"

    if args.iso:
        print(f"Scanning ISO: {args.iso}")
        extracted_dir = extract_iso(args.iso)
        if args.name is None:
            args.name = os.path.basename(extracted_dir)
            print(f"Found name: {args.name}")
        command.extend(["--source-name", args.name])
        output_file_prefix = "iso"
        command.extend(['scan', f"dir:{extracted_dir}"])
        #find images directory in extracted directory
        images_dir = os.path.join(extracted_dir, "images")
        if os.path.isdir(images_dir):
            print(f"Found images directory: {images_dir}")
            scan_images(images_dir)
        else:
            print(f"Images directory not found in: {extracted_dir}")

    if args.format:
        print(f"Output format: {args.format}")
        if args.version is None:
            args.version = "undefined"
            print(f"Version not provided, set to: {args.version}")

    format_output(command, args.format, output_file_prefix, args.name, args.version)
    run_syft_scan(command)

    if args.report:
        print(f"Generating vulnerability report")
        vuln_report(args.output_dir)

if __name__ == "__main__":
    scan()