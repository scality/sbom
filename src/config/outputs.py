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
    Create a standardized result dictionary for scanner outputs.

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
