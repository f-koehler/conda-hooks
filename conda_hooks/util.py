from __future__ import annotations

import json
import logging
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from yaml import CDumper as Dumper
from yaml import CLoader as Loader

LOGGER = logging.getLogger(__name__)
"""A logger to use throughout the module."""

ENV_DEFAULT_PATHS = [
    Path("environment.yml"),
    Path("environment.yaml"),
    Path("conda.yml"),
    Path("conda.yaml"),
]
"""Default names of the Anaconda environment file."""


class CondaHookError(Exception):
    pass


class NoCondaExecutableError(CondaHookError):
    def __init__(self):
        super().__init__("failed to find mamba/conda")


class EnvFileNotFoundError(CondaHookError):
    def __init__(self):
        super().__init__("failed to find env file")


class InvalidEnvFile(CondaHookError):
    def __init__(self, message: str):
        super().__init__(f"invalid env file: {message}")


class EnvDoesNotExistError(CondaHookError):
    def __init__(self, name: str):
        super().__init__(f"environment does not exist: {name}")


@lru_cache
def find_conda_executable() -> Path:
    """Find mamba/conda executable.

    This routine finds an executable to run conda commands. It prefers mamba since it
    is much faster for many operations. If mamba is not present in the PATH environment
    variable it will try to locate conda instead.

    Returns:
        Path of the mamba/conda executable.

    Raises:
        NoCondaExecutableError: If no mamba/conda executable was found.
    """
    result = shutil.which("mamba")
    if result:
        path = Path(result).resolve()
        LOGGER.info(f"found mamba: {path}")
        return path

    LOGGER.warn("did not find mamba, try to find conda (which might be slower)")

    if result:
        path = Path(result).resolve()
        LOGGER.info(f"found conda: {path}")
        return path

    raise NoCondaExecutableError()


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
                raise EnvFileNotFoundError()
        else:
            for default_path in ENV_DEFAULT_PATHS:
                if default_path.exists():
                    LOGGER.info("automatically found env file: {default_path}")
                    self.path = default_path
                    break
            else:
                raise EnvFileNotFoundError()

        # read env file
        with open(self.path) as fptr:
            self.content = yaml.load(fptr, Loader=Loader)

        # determine env name
        if "name" not in self.content:
            raise InvalidEnvFile("environment name missing")
        self.name = self.content["name"]

        # determine (pip) dependencies
        for dependency in self.content.get("dependencies", []):
            if isinstance(dependency, str):
                self.dependencies.append(dependency)
            elif isinstance(dependency, dict):
                if not isinstance(dependency["pip"], list):
                    raise InvalidEnvFile("pip dependencies should be a list")
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
        dependencies: list[str | dict[str, list[str]]]

        dependencies += self.dependencies
        if self.pip_dependencies:
            dependencies.append({"pip": self.pip_dependencies})

        content["dependencies"] = dependencies

        with open(path, "w") as fptr:
            yaml.dump(content, fptr, Dumper=Dumper)

    def exists(self) -> bool:
        environments = json.loads(
            subprocess.check_output(
                [find_conda_executable(), "env", "list", "--quiet", "--json"]
            )
            .decode()
            .strip()
        )
        for environment in environments:
            if Path(environment).name == self.name:
                return True

        return False

    def require_env_exists(self):
        if not self.exists():
            raise EnvDoesNotExistError(self.name)

    def export_env_dependencies(self) -> list[str]:
        self.require_env_exists()

        exported_environment: dict[str, Any] = yaml.load(
            subprocess.check_output(
                [
                    find_conda_executable(),
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

        return [
            dependency for dependency in exported_environment.get("dependencies", [])
        ]

    def update_env(self):
        self.require_env_exists()

        subprocess.run(
            [
                find_conda_executable(),
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
            return

        cmd = [
            str(find_conda_executable()),
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
            return

        subprocess.check_output(
            [
                find_conda_executable(),
                "env",
                "remove",
                "--quiet",
                "--name",
                self.name,
            ]
        )
