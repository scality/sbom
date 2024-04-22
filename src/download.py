import os
import argparse
from urllib.parse import urlparse
from requests import get
from requests.auth import HTTPBasicAuth

def download(url, username, password, output_dir, output_file):
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
    parser.add_argument("url")
    parser.add_argument("username", nargs='?', default=None)
    parser.add_argument("password", nargs='?', default=None)
    parser.add_argument("output_dir")
    parser.add_argument("output_file")
    args = parser.parse_args()

    download(args.url, args.username, args.password, args.output_dir, args.output_file)