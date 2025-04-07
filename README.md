# Generate SBOM GitHub Action

[![GitHub release](https://img.shields.io/github/release/scality/sbom.svg)](https://github.com/scality/sbom/releases/latest)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/scality/sbom/blob/main/LICENSE)

A GitHub Action for creating a software bill of materials (SBOM)
using [Syft](https://github.com/anchore/syft), with optional vulnerability scanning using [Grype](https://github.com/anchore/grype).

## Basic Usage

```yaml
- uses: scality/sbom@v2.0.0
  with:
    target: /usr/local/bin
```

This will create SBOM result file like `/tmp/sbom/bin_sbom.json` in the default output directory `/tmp/sbom`. 

## Configuration

### scality/sbom

The main [SBOM action](action.yaml) is responsible for generating SBOMs.

| Parameter            | Description                                                                                 | Default      |
| -------------------- | ------------------------------------------------------------------------------------------- | ------------ |
| `grype-version`      | Grype version to use                                                                        | `0.91.0`     |
| `syft-version`       | Syft version to use                                                                         | `1.22.0`     |
| `target`             | The target to scan (file, directory, image, ISO, or repo)                                   | `./`         |
| `target-type`        | Type of target to scan (file, directory, image, iso, repo)                                  | `file`       |
| `output-format`      | Format of the generated SBOM                                                              | `cyclonedx-json` |
| `output-file`        | A specific file location to store the SBOM                                                  |              |
| `output-dir`         | Directory to store generated SBOM files                                                     | `/tmp/sbom`  |
| `exclude-mediatypes` | Media types to exclude for images (comma-separated)                                         |              |
| `distro`             | Linux distribution of the target (if not auto-detected)                                     |              |
| `name`               | Override the detected name of the target                                                    |              |
| `version`            | Override the detected version of the target                                                 |              |
| `vuln`               | Enable vulnerability scanning                                                               | `false`      |
| `vuln-output-format` | Format for the vulnerability report (HTML or JSON) when `vuln` is enabled                     | `json`       |
| `vuln-output-file`   | A specific file location to store the vulnerability report                                  |              |

## Example Usage

### Scan with a specific format

Use the `output-format` and `vuln-output-format` parameters to choose the SBOM and vulnerability report formats:

```yaml
- uses: scality/sbom@v2.0.0
  with:
    target: ./artifacts
    output-format: cyclonedx-json  # SBOM format
    vuln: true                    # Enable vulnerability scanning
    vuln-output-format: html      # Vulnerability report format
```

### Specify target type explicitly

```yaml
- uses: scality/sbom@v2.0.0
  with:
    target: myimage.tar
    target-type: image
```

### Exclude mediatypes for container images

For images (like those built using Oras) that use custom mediatypes not supported by Skopeo:

```yaml
- uses: scality/sbom@v2.0.0
  with:
    target: ./images
    target-type: image
    exclude-mediatypes: "application/my-configuration+json,text/nginx-config"
```

### Enable vulnerability scanning

```yaml
- uses: scality/sbom@v2.0.0
  with:
    target: ./
    vuln: true
```

### Full Example

```yaml
name: "Generate SBOM"
on:
  workflow_dispatch:
  workflow_call:
jobs:
  generate-sbom:
    runs-on: ubuntu-22.04
    env:
      BASE_PATH: ${{ github.workspace }}/workdir
      SBOM_PATH: ${{ github.workspace }}/artifacts/sbom
    steps:
      - name: Create directories
        shell: bash
        run: |
          mkdir -p ${{ env.BASE_PATH }}/repo
          mkdir -p ${{ env.BASE_PATH }}/iso
          mkdir -p ${{ env.SBOM_PATH }}
          
      - name: Checkout repo for scanning
        uses: actions/checkout@v4  
        with:  
          fetch-depth: 0  
          fetch-tags: true
          path: ${{ env.BASE_PATH }}/repo/myrepo
          
      - name: Generate SBOM for repository
        uses: scality/sbom@v2.0.0
        with:
          target: ${{ env.BASE_PATH }}/repo/myrepo
          target-type: file
          output-dir: ${{ env.SBOM_PATH }}
          
      - name: Download artifacts
        shell: bash
        env:
          ARTIFACTS_URL: ${{ steps.artifacts.outputs.link }}
          ARTIFACTS_USER: ${{ secrets.ARTIFACTS_USER }}
          ARTIFACTS_PASSWORD: ${{ secrets.ARTIFACTS_PASSWORD }}
        run: |
          echo "Downloading my.iso from $ARTIFACTS_URL"
          curl -sSfL -o ${{ env.BASE_PATH }}/iso/my.iso -u $ARTIFACTS_USER:$ARTIFACTS_PASSWORD $ARTIFACTS_URL/my.iso
          
      - name: Generate SBOM for ISO
        uses: scality/sbom@v2.0.0
        with:
          target: ${{ env.BASE_PATH }}/iso/my.iso
          target-type: iso
          version: "1.0.0"
          output-dir: ${{ env.SBOM_PATH }}
          vuln: true
          
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: sbom-files
          path: ${{ env.SBOM_PATH }}/*.json
```

## CycloneDX Metadata

In the generated SBOM files, you will find CycloneDX metadata. Examples include:

- **For container images:**

```json
{
    "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
    "bomFormat": "CycloneDX",
    "specVersion": "1.6",
    "serialNumber": "urn:uuid:984d102d-0992-4dae-be80-ba551bc2079a",
    "version": 1,
    "metadata": {
        "timestamp": "2024-05-07T09:43:34Z",
        "tools": {
            "components": [
                {
                    "type": "application",
                    "author": "anchore",
                    "name": "syft",
                    "version": "1.21.0"
                }
            ]
        },
        "component": {
            "bom-ref": "1b58496ca93cc57d",
            "type": "container",
            "name": "my.iso:alpine",
            "version": "1.1.1"
        }
    }
}
```

- **For ISO files:**

```json
{
    "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
    "bomFormat": "CycloneDX",
    "specVersion": "1.6",
    "serialNumber": "urn:uuid:db2bc22b-a5e5-49a9-9d02-61a18480ead4",
    "version": 1,
    "metadata": {
        "timestamp": "2024-05-07T09:41:46Z",
        "tools": {
            "components": [
                {
                    "type": "application",
                    "author": "anchore",
                    "name": "syft",
                    "version": "1.21.0"
                }
            ]
        },
        "component": {
            "bom-ref": "4a057776eee09e2f",
            "type": "file",
            "name": "my.iso",
            "version": "1.0.0"
        }
    }
}
```

## References

HTML template for **Grype** vulnerability reports was modified from [Grype Contrib](https://github.com/opt-nc/grype-contribs).

## Core Workflow

```mermaid
flowchart TD
    subgraph inputs["Input Sources"]
        ENV["Environment Variables<br>INPUT_TARGET, INPUT_TARGET_TYPE, etc."]
    end

    subgraph core["Core Components"]
        CONFIG["config/inputs.py<br>get_inputs()"]
        MAIN["main.py<br>scan()"]
        PROVIDER_FACTORY["providers/base.py<br>get_provider()"]
    end

    subgraph providers["Providers Layer"]
        BASE_PROVIDER["providers/base.py<br>BaseProvider"]
        FILE_PROVIDER["providers/file.py<br>FileProvider"]
        ISO_PROVIDER["providers/iso.py<br>IsoProvider"]
        IMAGE_PROVIDER["providers/image.py<br>ImageProvider"]
    end

    subgraph tools["External Tools"]
        SYFT_TOOL["Syft CLI"]
        GRYPE_TOOL["Grype CLI"]
    end

    subgraph outputs["Output Files"]
        SBOM["SBOM File<br>/tmp/sbom/sbom_name_version.json"]
        VULN["Vulnerability Report<br>/tmp/sbom/vuln_name_version.json"]
    end

    ENV --> CONFIG
    CONFIG --> MAIN
    MAIN --> PROVIDER_FACTORY
    
    PROVIDER_FACTORY --> BASE_PROVIDER
    PROVIDER_FACTORY -- "target-type: file" --> FILE_PROVIDER
    PROVIDER_FACTORY -- "target-type: iso" --> ISO_PROVIDER
    PROVIDER_FACTORY -- "target-type: image" --> IMAGE_PROVIDER
    
    BASE_PROVIDER -- "sbom()" --> SYFT_TOOL
    BASE_PROVIDER -- "vuln()" --> GRYPE_TOOL
    
    SYFT_TOOL --> SBOM
    GRYPE_TOOL --> VULN
    SBOM -- "Input for vulnerability scan" --> GRYPE_TOOL
```

## Image Processing Workflow

```mermaid
flowchart TD
    subgraph inputs["Image Input Types"]
        REMOTE["Remote Image Reference<br>docker.io/library/alpine:latest"]
        TARBALL["Image Tarball<br>myimage.tar"]
        DIR["Directory of Images<br>/path/to/images/"]
    end
    
    subgraph detect["Detection & Preprocessing"]
        DISCOVER["_discover_images()"]
        MEDIATYPE["check_mediatype()"]
    end
    
    subgraph convert["Image Conversion"]
        CONVERT["convert_image_to_oci()"]
        SKOPEO["skopeo copy"]
    end
    
    subgraph process["Processing Path"]
        SINGLE["_scan_single_image()"]
        MULTI["_scan_image_directory()"]
        
        VULN_SINGLE["_scan_single_vuln()"]
        VULN_MULTI["_scan_multiple_vulns()"]
    end
    
    subgraph outputs["Output Files"]
        SINGLE_SBOM["Single SBOM<br>/tmp/sbom/image_name_version.json"]
        MULTI_SBOMS["Multiple SBOMs<br>/tmp/sbom/image_name_version.json"]
        
        SINGLE_VULN["Single Vuln Report<br>/tmp/sbom/image_name_version_vuln.json"]
        MULTI_VULNS["Multiple Vuln Reports<br>/tmp/sbom/image_name_version_vuln.json"]
    end
    
    REMOTE --> SINGLE
    TARBALL --> SINGLE
    DIR --> MULTI
    
    MULTI --> DISCOVER
    DISCOVER --> MEDIATYPE
    
    MEDIATYPE -- "Not excluded" --> CONVERT
    CONVERT --> SKOPEO
    
    SINGLE --> SYFT_TOOL
    SKOPEO --> SYFT_TOOL
    
    SYFT_TOOL --> SINGLE_SBOM
    SYFT_TOOL --> MULTI_SBOMS
    
    SINGLE_SBOM -- "If vuln=true" --> VULN_SINGLE
    MULTI_SBOMS -- "If vuln=true" --> VULN_MULTI
    
    VULN_SINGLE --> GRYPE_TOOL
    VULN_MULTI --> GRYPE_TOOL
    
    GRYPE_TOOL --> SINGLE_VULN
    GRYPE_TOOL --> MULTI_VULNS
```

## Data Flow Explanation

### Input Processing

1. Environment variables (from GitHub Actions) are read by `config/inputs.py`.
2. CLI arguments are processed by Click in `main.py`.
3. The input sources are combined with CLI arguments taking precedence.

### Provider Selection & SBOM Generation

1. The target type is determined from the provided inputs.
2. The `get_provider()` factory function selects the appropriate provider.
3. The provider’s `sbom()` method invokes Syft to generate the SBOM, which is saved with a standardized naming scheme: `{target_type}_{name}_{version}.json`.

### Vulnerability Scanning (if enabled)

1. If `vuln` is enabled, the provider’s `vuln()` method uses Grype to scan the SBOM.
2. Grype generates a vulnerability report saved as: `{target_type}_{name}_{version}_vuln.json`.
