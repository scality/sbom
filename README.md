# Generate SBOM GitHub Action

This action generates a Software Bill of Materials (SBOM) from git repositories using [Syft](https://github.com/anchore/syft).

## Inputs

### `ref`

The git revision to checkout. Default is the current commit SHA.

### `repo`

The repository to scan. This is required.

### `input_path`

The path to the repository. This is required.

### `output_path`

The path to store the SBOM. This is required.

## Example usage

```yaml
uses: scality/sbom@v1
with:
  ref: ${{ github.sha }}
  repo: 'your-repo-to-scan'
  input_path: 'path-to-your-repo'
  output_path: 'path-to-store-sbom'
