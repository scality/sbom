import argparse
import os
from urllib.parse import urlparse
from requests import get
from requests.auth import HTTPBasicAuth

def download(url, username, password, output_dir, output_file):
    """
    ## This function downloads a file from a URL.

    ### Args:
        - `url (string)`: URL to download the file from
        - `username (string)`: Username for authentication
        - `password (string)`: Password for authentication
        - `output_dir (string)`: Directory to store the downloaded file
        - `output_file (string)`: Name of the downloaded file
    """
    url = os.environ.get("INPUT_URL")
    username = os.environ.get("INPUT_USERNAME")
    password = os.environ.get("INPUT_PASSWORD")
    output_dir = os.environ.get("INPUT_OUTPUT_DIR")
    output_file = os.environ.get("INPUT_OUTPUT_FILE")

    if output_file is None:
        output_file = os.path.basename(urlparse(url).path)
    print(f"Downloading {output_file} to {output_dir}")
    
    #ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)
    if username is not None and password is not None:
        response = get(url, auth=HTTPBasicAuth(username, password))
    else:
        response = get(url)
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
        "output_dir"
        )
    parser.add_argument(
        "output_file",
        nargs='?',
        default=None
    )
    args = parser.parse_args()

    download(args.url, args.username, args.password, args.output_dir, args.output_file)
