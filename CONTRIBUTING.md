# Contributing

Contributions are welcome! Please follow the guidelines below.

## Codespaces

This project is configured to work with GitHub Codespaces. To open the project in a Codespace, click the button below:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/scality/sbom)

## Environment variables

Example environment variables for running the action locally:

```python
import os
###########################
##### DEV ENVIROMENT ######
### FILE
os.environ["INPUT_TARGET"] = "samples/curl-7.61.1-34.el8_10.3.x86_64.rpm"
os.environ["INPUT_TARGET_TYPE"] = "file"
### IMAGE
os.environ["INPUT_TARGET_TYPE"] = "image"
os.environ["INPUT_TARGET"] = "cr.fluentbit.io/fluent/fluent-bit:3.0.0"
### ISO
os.environ["INPUT_TARGET_TYPE"] = "iso"
os.environ["INPUT_TARGET"] = "samples/Core-15.0.iso"
##############################
os.environ["INPUT_OUTPUT_FORMAT"] = "cyclonedx-json"
os.environ["INPUT_VULN"] = "true"
os.environ["INPUT_VULN_OUTPUT_FORMAT"] = "html,cyclonedx-json"
##########################
```

## Run the action locally

`act` can be used to run the GitHub Actions workflow locally.
It has been installed through the `gh` extension.
To run the workflow locally, execute the following command:

```bash
docker login ghcr.io
gh extension install https://github.com/nektos/gh-act
gh act push --rm --workflows=.github/workflows/tests.yaml -P ubuntu-24.04=ghcr.io/catthehacker/ubuntu:act-22.04
```

For more information on how to use `act`, please refer to the [official documentation] or run `gh act --help`.

[official documentation]: https://nektosact.com/introduction.html
