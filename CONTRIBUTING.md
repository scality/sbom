# Contributing

Contributions are welcome! Please follow the guidelines below.

## Codespaces

This project is configured to work with GitHub Codespaces. To open the project in a Codespace, click the button below:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/scality/sbom)

## Run the action locally

`act` can be used to run the GitHub Actions workflow locally.
It has been installed through the `gh` extension.
To run the workflow locally, execute the following command:

```bash
gh act push --rm --workflows=.github/workflows/tests.yaml -P ubuntu-22.04=ghcr.io/catthehacker/ubuntu:act-22.04
```

For more information on how to use `act`, please refer to the [official documentation] or run `gh act --help`.

[official documentation]: https://nektosact.com/introduction.html
