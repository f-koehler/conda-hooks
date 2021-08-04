from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

import yaml
from yaml import CDumper as Dumper
from yaml import CLoader as Loader

from . import errors, util

LOGGER = logging.getLogger(__name__)
"""A logger to use throughout the module."""

ENV_DEFAULT_PATHS = [
    Path("environment.yml"),
    Path("environment.yaml"),
    Path("conda.yml"),
    Path("conda.yaml"),
]
"""Default names of the Anaconda environment file."""


class EnvironmentFile:
    def __init__(self, path: Path | str | None = None):
        self.path: Path
        self.name: str
        self.content: dict[str, Any] = {}
        self.dependencies: list[str] = []
        self.pip_dependencies: list[str] = []
        self.channels: list[str] = []

        # determine path of env file
        if path is not None:
            path = Path(path)
            if path.exists():
                self.path = path
            else:
                raise errors.EnvFileNotFoundError()
        else:
            for default_path in ENV_DEFAULT_PATHS:
                if default_path.exists():
                    LOGGER.info("automatically found env file: {default_path}")
                    self.path = default_path
                    break
            else:
                raise errors.EnvFileNotFoundError()

        # read env file
        with open(self.path) as fptr:
            self.content = yaml.load(fptr, Loader=Loader)

        # determine env name
        if "name" not in self.content:
            raise errors.InvalidEnvFile("environment name missing")
        self.name = self.content["name"]

        # determine (pip) dependencies
        for dependency in self.content.get("dependencies", []):
            if isinstance(dependency, str):
                self.dependencies.append(dependency)
            elif isinstance(dependency, dict):
                if not isinstance(dependency["pip"], list):
                    raise errors.InvalidEnvFile("pip dependencies should be a list")
                else:
                    for pip_dependency in dependency["pip"]:
                        self.pip_dependencies.append(pip_dependency)

        self.dependencies.sort()
        self.pip_dependencies.sort()

        # read channels
        self.channels = self.content.get("channels", [])

    def write(self, path: Path | None = None):
        if path is None:
            path = self.path

        content: dict[str, Any] = {"name": self.name}
        if self.channels:
            content["channels"] = self.channels
        dependencies: list[str | dict[str, list[str]]] = []

        dependencies += self.dependencies
        if self.pip_dependencies:
            dependencies.append({"pip": self.pip_dependencies})

        content["dependencies"] = dependencies

        with open(path, "w") as fptr:
            yaml.dump(content, fptr, Dumper=Dumper)

    def exists(self) -> bool:
        environments = json.loads(
            subprocess.check_output(
                [util.find_conda_executable(), "env", "list", "--quiet", "--json"]
            )
            .decode()
            .strip()
        )["envs"]
        for environment in environments:
            if Path(environment).name == self.name:
                return True

        return False

    def require_env_exists(self):
        if not self.exists():
            raise errors.EnvDoesNotExistError(self.name)

    def get_installed_dependencies(self) -> list[str]:
        self.require_env_exists()

        exported_environment: dict[str, Any] = yaml.load(
            subprocess.check_output(
                [
                    util.find_conda_executable(),
                    "env",
                    "export",
                    "--from-history",
                    "--quiet",
                    "--name",
                    self.name,
                ],
            ),
            Loader=Loader,
        )

        dependencies = [
            dependency for dependency in exported_environment.get("dependencies", [])
        ]
        dependencies.sort()
        return dependencies

    def update_env(self):
        self.require_env_exists()

        subprocess.run(
            [
                util.find_conda_executable(),
                "env",
                "update",
                "--quiet",
                "--name",
                self.name,
                "--file",
                self.path,
            ],
        )

    def create(self):
        if self.exists():
            LOGGER.warning(f"environment {self.name} exists, do not create")
            return

        cmd = [
            str(util.find_conda_executable()),
            "env",
            "create",
            "--quiet",
            "--name",
            self.name,
            "--file",
            str(self.path),
        ]

        subprocess.check_output(cmd)

    def remove(self):
        if not self.exists():
            LOGGER.warning(f"environment {self.name} does not exists, do not remove")
            return

        subprocess.check_output(
            [
                util.find_conda_executable(),
                "env",
                "remove",
                "--quiet",
                "--name",
                self.name,
            ]
        )
