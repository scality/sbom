"""Module providing conversion of images"""

import os
import subprocess
import tarfile
import json
import logging


def detect_image_origin(path):
    """
    ## Detects the origin of an image based on the presence of certain files.
    ### Args:
        path (str): The path to the image.
    ### Returns:
        str: The type of image ("docker", "oci", or "unknown").
    """
    logging.info("Detecting image origin for: %s", path)
    if os.path.isdir(path):
        if os.path.isfile(os.path.join(path, "oci-layout")):
            logging.info("%s is an OCI image.", path)
            return "oci"

        if os.path.isfile(os.path.join(path, "manifest.json")):
            logging.info("%s is a Docker image.", path)
            return "docker"

    if path.endswith(".tar"):
        with tarfile.open(path) as tar:
            for member in tar.getmembers():
                if member.name == "manifest.json":
                    logging.info("%s is a Docker image.", path)
                    return "docker"
                if member.name.startswith("blobs/"):
                    logging.info("%s is an OCI image.", path)
                    return "oci"
    return "unknown"


def convert_image_to_oci(image_dir, convert_dir):
    """
    ## Converts a Docker image to OCI format.
    ### Args:
        image_dir (str): The path to the Docker image.
        convert_dir (str): The path to the directory where the OCI image will be saved.
    ### Returns:
        str: The path to the converted OCI image.
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
        logging.info(
            "Converted %s to OCI format at: %s", image_dir, converted_image_dir
        )
        return converted_image_dir

    if detect_image_origin(image_dir) == "oci":
        logging.info("%s is already in OCI format.", image_dir)
        return image_dir  # Return the original path since it's already OCI

    logging.warning("Failed to convert %s: Unknown format.", image_dir)
    return image_dir  # Return the original path if format is unknown


def check_mediatype(image_dir, excluded_mediatypes=None):
    """
    ## Gets the media type of an image.
    ### Args:
        image_dir (str): The path to the image.
        excluded_mediatypes (list): A list of media types to exclude.
    ### Returns:
        bool: True if the image has excluded media types, False otherwise.
    """
    excluded = False
    if excluded_mediatypes:
        inspect_command = f"skopeo inspect dir:{image_dir} --raw"
        logging.info("Running command: %s", inspect_command)
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

        excluded_types = [
            media_type
            for media_type in media_types
            if media_type in excluded_mediatypes
        ]

        if excluded_types:
            logging.info(
                "Excluded media types found: %s in %s", excluded_types, image_dir
            )
            excluded = True
        else:
            logging.info("No excluded media types found in %s", image_dir)
            excluded = False

    return excluded
