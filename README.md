# conda-hooks

Keep anaconda environment files up to date with installed packages.
In contrast to `conda export` it keeps the channel list intact, sorts packages alphabetically and does not purge `pip` dependencies.
`conda-hooks` can be integrated easily with [pre-commit](https://pre-commit.com/) hooks to automatically check for any missing packages before committing.

[![Build Status](https://img.shields.io/github/workflow/status/f-koehler/conda-hooks/build)](https://github.com/f-koehler/conda-hooks/actions)
[![codecov](https://codecov.io/gh/f-koehler/conda-hooks/branch/main/graph/badge.svg?token=4XHPAHUDOL)](https://codecov.io/gh/f-koehler/conda-hooks)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/f-koehler/conda-hooks/main.svg)](https://results.pre-commit.ci/latest/github/f-koehler/conda-hooks/main)
[![PyPI Version](https://img.shields.io/pypi/v/conda-hooks)](https://pypi.org/project/conda-hooks/)
![License](https://img.shields.io/pypi/l/conda-hooks?color=blue)

## Installation

### As a Python package

The `conda_hooks` package is installable as a normal python package, for example via pip:

```bash
pip install conda_hooks
```

### As a `pre-commit` hook

In your `.pre-commit-config.yaml` file add

```yaml
repos:
  - repo: https://github.com/f-koehler/conda-hooks
    rev: "0.4.2"
    hooks:
      - id: conda-env-store
```

## Usage

### Command line

Running `env_store --help` will print information about the available command line options.
We can either specify paths to environment file explicitly

```bash
conda_env_store environment1.yml env2.yaml src/env3.yml
```

or use globbing patterns like this:

```bash
conda_env_store -g **/environment.yml -g **/env.yml
```

Of course we can combine both methods:

```bash
conda_env_store -g src/env*.yml environment.yml
```

### As a `pre-commit` hook

When using the `pre-commit` hook we can use the same command line arguments, so please refer to the section above.
An example using globbing patterns would be:

```yaml
repos:
  - repo: https://github.com/f-koehler/conda-hooks
    rev: "0.4.1"
    hooks:
      - id: prettier
        args: ["-g", "**/environment.yml"]
```
