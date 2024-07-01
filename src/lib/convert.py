"""Module providing conversion of images"""

import os
import subprocess
import tarfile
import json


def detect_image_origin(path):
    """
    ## Detects the origin of an image based on the presence of certain files.
    ### Args:
        path (str): The path to the image.
    """
    print(f"Detecting image origin for: {path}")
    if os.path.isdir(path):
        if os.path.isfile(os.path.join(path, "oci-layout")):
            print(f"{path} is an OCI image.")
            return "oci"
        elif os.path.isfile(os.path.join(path, "manifest.json")):
            print(f"{path} is a Docker image.")
            return "docker"
    if path.endswith(".tar"):
        with tarfile.open(path) as tar:
            for member in tar.getmembers():
                if member.name == "manifest.json":
                    print(f"{path} is a Docker image.")
                    return "docker"
                elif member.name.startswith("blobs/"):
                    print(f"{path} is an OCI image.")
                    return "oci"
    return "unknown"


def convert_image_to_oci(image_dir, convert_dir):
    """
    ## Converts a Docker image to OCI format.
    ### Args:
        image_dir (str): The path to the Docker image.
        convert_dir (str): The path to the directory where the OCI image will be saved.
    """
    image_basename = os.path.basename(image_dir)
    converted_image_dir = f"/tmp/images/{image_basename}"
    if convert_dir is not None:
        converted_image_dir = convert_dir
        os.makedirs(converted_image_dir, exist_ok=True)
    if detect_image_origin(image_dir) == "docker":
        subprocess.run(
            [
                "skopeo",
                "copy",
                f"dir:{image_dir}",
                f"oci:{converted_image_dir}",
                "--format",
                "oci",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        print(f"Converted {image_dir} to OCI format at: {converted_image_dir}")
        return converted_image_dir
    elif detect_image_origin(image_dir) == "oci":
        print(f"{image_dir} is already in OCI format.")
    else:
        print(f"{image_dir} is not in a recognized format.")


def check_mediatype(image_dir, excluded_mediatypes=None):
    """
    ## Gets the media type of an image.
    ### Args:
        image_dir (str): The path to the image.
        excluded_mediatypes (list): A list of media types to exclude.
    """
    excluded = False
    if excluded_mediatypes:
        inspect_command = f"skopeo inspect dir:{image_dir} --raw"
        print(f"Running command: {inspect_command}")
        result = subprocess.run(
            inspect_command, capture_output=True, text=True, check=True, shell=True
        )
        data = json.loads(result.stdout)
        media_types = []
        if "config" in data and "mediaType" in data["config"]:
            media_types.append(data["config"]["mediaType"])
        if "layers" in data:
            for layer in data["layers"]:
                if "mediaType" in layer:
                    media_types.append(layer["mediaType"])
        # Use a set to collect unique excluded media types
        excluded_types = set([
            media_type
            for media_type in media_types
            if media_type in excluded_mediatypes
        ])
        if excluded_types:
            print(f"Excluded media types found: {list(excluded_types)} in {image_dir}")
            excluded = True
        else:
            print("No excluded media types found, continuing.")
            excluded = False
    return excluded
