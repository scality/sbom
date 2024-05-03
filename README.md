# Generate SBOM GitHub Action

[![GitHub release](https://img.shields.io/github/release/scality/sbom.svg)](https://github.com/scality/sbom/releases/latest)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/anchore/sbom-action/blob/main/LICENSE)

A GitHub Action for creating a software bill of materials (SBOM)
using [Syft](https://github.com/anchore/syft).

## Basic Usage

```yaml
- uses: scality/sbom@v1
  with:
    target: ./
```

This will create SBOM result files based on type, ex: 

- repo_sbom_v1.1.0-4-gd6cdf1f.json
- repo_sbom_v1.2.0.json
- image_nginx_latest.json
- iso_myiso.iso_128.json

If you want to scan a repository, you have to checkout it with `fetch-tags`.
This is mandatory to get repo version for SBOM filename. 

```yaml
- uses: actions/checkout@v4  
  with:  
    fetch-depth: 0  
    fetch-tags: true  
```

## Configuration

### scality/sbom

The main [SBOM action](action.yml), responsible for generating SBOMs.

| Parameter                   | Description                                                                           | Default                |
| --------------------------- | ------------------------------------------------------------------------------------- | ---------------------- |
| `grype-version`             | Grype version to use                                                                  | 0.77.2                 |
| `sfyt-version`              | Syft version to use                                                                   | 1.2.0                  |
| `trivy-version`             | Trivy version to use                                                                  | 0.50.1                 |
| `target`                    | A file/directory/iso on the filesystem to scan.                                       | \<current directory>   |
| `format`                    | Format of SBOM file.                                                                  | cyclonedx-json         |
| `name`                      | Name of the target, if you need to overwrite the detected.                            |                        |
| `version`                   | Version of the target, if you need to overwrite the detected. ISO have no version.    |                        |
| `output_dir`                | Path to store generated SBOM files.                                                   | /tmp/sbom              |
| `exclude_mediatypes`        | Media types to exclude for images.                                                    |                        |
| `vuln_report`               | Generate vuln report using Grype.                                                     |                        |

## Example Usage

### Scan with a specific format

Use the `path` parameter, relative to the repository root:

```yaml
- uses: scality/sbom@v1
  with:
    target: ./artifacts
    format: cyclonedx-json
```

### Exclude mediatypes for container images

Images created with Oras for example have custom mediatype and are not usable
by Skopeo, they have to be excluded. 

```yaml
- uses: scality/sbom@v1
  with:
    target: ./images
    exclude_mediatypes: "application/grafana-dashboard+json text/nginx-conf-template"
```

### Full example

```yaml
name: "Generate sbom"
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
      - name: Generate sbom for repository
        uses: scality/sbom@v1.2.0
        with:
          target: ${{ env.BASE_PATH }}/repo/myrepo
          output-dir: ${{ env.SBOM_PATH }}
      - name: Get artifacts URL
        uses: scality/action-artifacts@v4
        id: artifacts
        with:
          method: setup
          url: https://artifactmanager.net
          user: ${{ secrets.ARTIFACTS_USER }}
          password: ${{ secrets.ARTIFACTS_PASSWORD }}
      - name: Donwload artifacts
        shell: bash
        env:
          ARTIFACTS_URL: ${{ steps.artifacts.outputs.link }}
          ARTIFACTS_USER: ${{ secrets.ARTIFACTS_USER }}
          ARTIFACTS_PASSWORD: ${{ secrets.ARTIFACTS_PASSWORD }}
        run: |
          echo "Downloading my.iso from $ARTIFACTS_URL"
          curl -sSfL -o ${{ env.BASE_PATH }}/iso/my.iso -u $ARTIFACTS_USER:$ARTIFACTS_PASSWORD $ARTIFACTS_URL/my.iso
      - name: Generate sbom for ISO
        uses: scality/sbom@v1.2.0
        with:
          target: ${{ env.BASE_PATH }}/iso/my.iso
          version: "1.0.0"  # Make sure to replace this with the actual ISO version
          output-dir: ${{ env.SBOM_PATH }}
      - name: Generate archive
        shell: bash
        run: |
          cd ${{ env.SBOM_PATH }}
          tar -czf sbom_myproject.tar.gz *.json
      - name: Clean up
        shell: bash
        run: |
          rm -rf ${{ env.BASE_PATH }}/repo
          rm -rf ${{ env.BASE_PATH }}/iso
          rm -f ${{ env.SBOM_PATH }}/*.json
      - name: Upload artifacts
        if: always()
        uses: scality/action-artifacts@v4
        with:
          method: upload
          url: https://artifactmanager.net
          user: ${{ secrets.USER }}
          password: ${{ secrets.PASSWORD }}
          source: artifacts
```

## References

HTML template for **Grype** results visualisation was slightly modified from [Grype Contrib](https://github.com/opt-nc/grype-contribs).
