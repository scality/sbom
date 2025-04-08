"""Base scanner functionality shared between scanners."""


def create_standard_result(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    scanner: str,
    success: bool = True,
    target: str = None,
    name: str = None,
    version: str = None,
    sbom_path: str = None,
    stdout: str = None,
    additional: dict = None,
    error: str = None,
):
    """
    ## Create a standardized result dictionary for scanner outputs.
    ## Args:
        scanner (str): The name of the scanner.
        success (bool): Indicates if the scan was successful.
        target (str): The target that was scanned.
        name (str): The name of the target.
        version (str): The version of the target.
        sbom_path (str): The path to the SBOM file.
        stdout (str): The standard output from the scanner.
        additional (dict): Additional information to include in the result.
        error (str): Error message if any occurred during scanning.
    ## Returns:
        dict: A dictionary containing the standardized result.
    ## Information:
        Returns a flat JSON structure that is easy to parse.
    """
    result = {
        "scanner": scanner,
        "success": success,
        "target": target,
        "name": name,
        "version": version,
        "sbom_path": sbom_path,
    }
    if stdout:
        result["stdout"] = stdout
    if additional and isinstance(additional, dict):
        result.update(additional)
    if error:
        result["error"] = error
    return result
