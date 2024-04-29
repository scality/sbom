import os
import subprocess
import tarfile
import json

def detect_image_origin(path):
    print(f"Detecting image origin for: {path}")
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

def convert_image_to_oci(image_dir, convert_dir):
    image_basename = os.path.basename(image_dir)
    converted_image_dir = f"/tmp/images/{image_basename}"
    if convert_dir is not None:
        converted_image_dir = convert_dir
        os.makedirs(converted_image_dir, exist_ok=True)
    if detect_image_origin(image_dir) == 'docker':
        subprocess.run(["skopeo", "copy", f"dir:{image_dir}", f"oci:{converted_image_dir}", "--format", "oci"])
        print(f"Converted {image_dir} to OCI format at: {converted_image_dir}")
        return converted_image_dir
    elif detect_image_origin(image_dir) == 'oci':
        print(f"{image_dir} is already in OCI format.")
    else:
        print(f"{image_dir} is not in a recognized format.")

def get_mediatype(image_dir, excluded_mediatypes=None):
    excluded = False
    if excluded_mediatypes is not None:
        excluded_media_types = excluded_mediatypes
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