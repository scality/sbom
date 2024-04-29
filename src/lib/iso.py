import os
import subprocess

def extract_iso(iso_path):
    #create temporary directory to extract iso
    iso_basename = os.path.basename(iso_path)
    extracted_dir = f"/tmp/{iso_basename}"
    os.makedirs(extracted_dir, exist_ok=True)
    subprocess.run(["7z", "x", iso_path, f"-o{extracted_dir}"])
    print(f"Extracted ISO to: {extracted_dir}")
    return extracted_dir

def image_dir_present(extracted_dir):
    #check if image directory is present
    image_dir = os.path.join(extracted_dir, "images")
    if not os.path.isdir(image_dir):
        return None
    return image_dir