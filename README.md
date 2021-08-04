# conda-hooks

Keep anaconda environment files up to date with installed packages.
This can easily be automated using [pre-commit](https://pre-commit.com/) hooks.

[![Build Status](https://img.shields.io/github/workflow/status/f-koehler/conda-hooks/build)](https://github.com/f-koehler/conda-hooks/actions)
[![codecov](https://codecov.io/gh/f-koehler/conda-hooks/branch/main/graph/badge.svg?token=4XHPAHUDOL)](https://codecov.io/gh/f-koehler/conda-hooks)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/f-koehler/conda-hooks/main.svg)](https://results.pre-commit.ci/latest/github/f-koehler/conda-hooks/main)
[![PyPI Version](https://img.shields.io/pypi/v/conda-hooks)](https://pypi.org/project/conda-hooks/)
![License](https://img.shields.io/pypi/l/conda-hooks?color=blue)

## Installation

### As a python package

The `conda_hooks` package is installable as a normal python package, for example via pip:

```bash
pip install conda_hooks
```

### As a `pre-commit` hook

In your `.pre-commit-config.yaml` file add

```yaml
repos:
  - repo: https://github.com/f-koehler/conda-hooks
    rev: "0.2.2"
    hooks:
      - id: prettier
```

## Usage/Examples

TODO
