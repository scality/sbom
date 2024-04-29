import os
import subprocess
from git import Repo, exc

target_type = "path"

def is_git_repo(target):
    try:
        _ = Repo(target).git_dir
        return True
    except exc.InvalidGitRepositoryError:
        return False

def get_repo_name(target):
    origin = subprocess.check_output(["git", "-C", target, "config", "--get", "remote.origin.url"], text=True).strip()
    name = origin.split("/")[-1].replace(".git", "")
    return name

def get_repo_version(target):
    version = subprocess.check_output(["git", "-C", target, "describe", "--tags"], text=True).strip()
    return version

def detect_target_type(target):
    global target_type
    if target.endswith(".iso"):
        target_type = "iso"
        print("Detected iso file.")
        name = os.path.basename(target)
        version = os.environ.get("INPUT_VERSION")
        if version is None:
            version = "undefined"
        else:
            version = version
    elif os.path.isdir(target):
        target_type = "directory"
        print("Detected directory.")
        if is_git_repo(target):
            version = get_repo_version(target)
            name = get_repo_name(target)
            target_type = "git"
            print(f"Detected git repository: {name}, version: {version}")
        else:
            name = os.path.basename(target)
            version = os.environ.get("INPUT_VERSION")
            if version is None:
                version = "undefined"
            else:
                version = version
    return {"target_type": target_type, "name": name, "version": version}
