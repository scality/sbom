"""Module providing detection of target"""
import os
from git import Repo, exc

TARGET_TYPE = "path"

def is_git_repo(target):
    """
    ## Check if a directory is a git repository.
    ### Args:
        target (str): The path to the directory.
    """
    try:
        _ = Repo(target).git_dir
        return True
    except exc.InvalidGitRepositoryError:
        return False

def get_repo_name(target):
    """
    ## Get the name of a git repository.
    ### Args:
        target (str): The path to the git repository.
    """
    name = Repo(target).remotes.origin.url.split(".git")[0].split("/")[-1]
    return name

def get_repo_version(target):
    """
    ## Get the version of a git repository.
    ### Args:
        target (str): The path to the git repository.
    """
    version = Repo(target).git.describe(tags=True)
    return version

def detect_target_type(target):
    """
    ## Detect the type of target. ISO or directory.
    ### Args:
        target (str): The path to the target.
    """
    target_type = "path"
    if target.endswith(".iso"):
        target_type = "iso"
        print("Detected iso file.")
        if os.environ.get("NAME"):
            name = os.environ.get("NAME")
        else:
            name = os.path.basename(target)
        if os.environ.get("VERSION"):
            version = os.environ.get("VERSION")
        else:
            version = "undefined"
    elif os.path.isdir(target):
        target_type = "directory"
        print("Detected directory.")
        print(f"Provided target: {target}")
        if is_git_repo(target):
            version = get_repo_version(target)
            name = get_repo_name(target)
            target_type = "git"
            print(f"Detected git repository: {name}, version: {version}")
        else:
            name = os.path.basename(target)
            version = "undefined"
        if os.environ.get("VERSION"):
            version = os.environ.get("VERSION")
    return {"target_type": target_type, "name": name, "version": version}
