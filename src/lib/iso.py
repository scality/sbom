"""Module providing iso extraction for scanning"""
import os
from pyunpack import Archive

def extract_iso(iso_path):
    """
    ## Extracts an ISO file to a temporary directory.
    ### Args:
        iso_path (str): The path to the ISO file.
    """
    #create temporary directory to extract iso
    iso_basename = os.path.basename(iso_path)
    extracted_dir = f"/tmp/extracted/{iso_basename}"
    os.makedirs(extracted_dir, exist_ok=True)
    Archive(iso_path).extractall(extracted_dir)
    print(f"Extracted ISO to: {extracted_dir}")
    return extracted_dir

def image_dir_present(extracted_dir):
    """
    ## Checks if the extracted directory contains an image directory.
    ### Args:
        extracted_dir (str): The path to the extracted directory.
    """
    #check if image directory is present
    image_dir = os.path.join(extracted_dir, "images")
    if not os.path.isdir(image_dir):
        return None
    return image_dir
