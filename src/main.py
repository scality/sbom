"""Main entry point for the SBOM Github Action."""

import logging
import sys
import click
from config.inputs import get_inputs
from modules.install import install_tool
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
    ### This command is used to install the required tools.
    """
    click.echo("Installing requirements...")
    # Get the inputs from the Github action
    inputs = get_inputs()

    # Filter to only include tool versions
    tool_versions = {
        "syft_version": inputs.get("syft_version"),
        "grype_version": inputs.get("grype_version"),
    }

    install_tool(tool_versions)


@cli.command()
def scan():
    """
    ## Scan a target.
    ### This command is used to scan a target and generate an SBOM.
    """
    # Get the inputs from the Github action
    inputs = get_inputs()

    try:
        # Get the appropriate provider based on inputs
        provider = get_provider(inputs)

        # Always generate the SBOM first
        sbom_result = provider.sbom(inputs)
        click.echo(f"SBOM generated: {sbom_result}")

        # Track what we need to scan for vulnerabilities
        sboms_to_scan = [sbom_result]

        # Merge if requested
        if inputs.get("merge"):
            merged_sbom = provider.merge(sbom_result)
            click.echo(f"SBOM merged: {merged_sbom}")
            # Add merged SBOM to vulnerability scan targets
            sboms_to_scan.append(merged_sbom)

        # Run vulnerability scanning if enabled
        if inputs.get("vuln"):
            for sbom in sboms_to_scan:
                is_merged = sbom != sbom_result
                vuln_report = provider.vuln(sbom)
                sbom_type = "merged " if is_merged else ""
                click.echo(
                    f"Vulnerability report generated for {sbom_type}SBOM: {vuln_report}"
                )

    except (ValueError, FileNotFoundError, RuntimeError) as error:
        logging.error("Scan failed: %s", error)
        sys.exit(1)


if __name__ == "__main__":
    cli()
