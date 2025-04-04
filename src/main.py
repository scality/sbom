"""Main entry point for the SBOM Github Action."""

import logging
import sys
import click
from config.inputs import get_inputs
from modules.install import install_scanners
from providers.factory import get_provider

# Configure logging to show INFO level messages
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s][%(name)s][%(funcName)s] %(levelname)s: %(message)s",
)


@click.group()
@click.version_option()
def cli():
    """
    # SBOM Github Action CLI
    This is a command line interface for the SBOM Github Action.
    It allows you to install the required scanners and scan a target.
    """
    click.echo("Welcome to the SBOM Github Action CLI!")


@cli.command()
def install():
    """
    ## Install the requirements.
    ### This command is used to install the required scanners.
    """
    click.echo("Installing requirements...")
    # Get the inputs from the Github action
    inputs = get_inputs()

    # Filter to only include scanner versions
    scanner_versions = {
        "syft_version": inputs.get("syft_version"),
        "grype_version": inputs.get("grype_version"),
    }

    install_scanners(scanner_versions)


@cli.command()
def scan():
    """
    ## Scan a target.
    ### This command is used to scan a target and generate an SBOM.
    """
    # Get the inputs from the Github action
    inputs = get_inputs()

    #################### TODELETE
    # Debug all inputs
    print(f"DEBUG - All inputs: {inputs}")
    print(f"DEBUG - Target: {inputs.get('target')}")
    print(f"DEBUG - Target Type: {inputs.get('target_type')}")
    #################### TODELETE

    try:
        # Get the appropriate provider based on inputs
        provider = get_provider(inputs)

        sbom_result = provider.sbom(inputs)
        click.echo(f"SBOM generated: {sbom_result}")

        # If vulnerability scanning is enabled, run the scanner
        if inputs.get("vuln"):
            vuln_report = provider.vuln(sbom_result)
            click.echo(f"Vulnerability report generated: {vuln_report}")

    except (ValueError, FileNotFoundError, RuntimeError) as error:
        logging.error("Scan failed: %s", error)
        sys.exit(1)


if __name__ == "__main__":
    cli()
