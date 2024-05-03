"""Module providing artifact downloading"""
import argparse
import os
from urllib.parse import urlparse
from requests import get
from requests.auth import HTTPBasicAuth

def download(url, username, password, output_dir, output_file):
    """
    ## This function downloads a file from a URL.

    ### Args:
        url (string): URL to download the file from
        username (string): Username for authentication
        password (string): Password for authentication
        OUTPUT_DIR (string): Directory to store the downloaded file
        output_file (string): Name of the downloaded file
    """
    if os.environ.get("URL") is not None and os.environ.get("URL") != "None":
        url = os.environ.get("URL")
    if os.environ.get("USERNAME") is not None and os.environ.get("USERNAME") != "None":
        username = os.environ.get("USERNAME")
    if os.environ.get("PASSWORD") is not None and os.environ.get("PASSWORD") != "None":
        password = os.environ.get("PASSWORD")
    if os.environ.get("OUTPUT_DIR") is not None and os.environ.get("OUTPUT_DIR") != "None":
        output_dir = os.environ.get("OUTPUT_DIR")
    if os.environ.get("OUTPUT_FILE") is not None and os.environ.get("OUTPUT_FILE") != "None":
        output_file = os.environ.get("OUTPUT_FILE")

    if output_file is None:
        output_file = os.path.basename(urlparse(url).path)
    print(f"Downloading {output_file} to {output_dir}")

    #ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)
    if username is not None and password is not None:
        response = get(url, auth=HTTPBasicAuth(username, password), timeout=10)
    else:
        response = get(url, timeout=10)
    with open(output_path, 'wb') as file:
        file.write(response.content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url"
        )
    parser.add_argument(
        "username",
        nargs='?',
        default=None
        )
    parser.add_argument(
        "password",
        nargs='?',
        default=None
        )
    parser.add_argument(
        "OUTPUT_DIR"
        )
    parser.add_argument(
        "output_file",
        nargs='?',
        default=None
    )
    args = parser.parse_args()

    download(args.url, args.username, args.password, args.OUTPUT_DIR, args.output_file)
