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
def find_conda() -> Path:
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
    def __init__(self, path: Path | None = None):
        self.path: Path
        self.name: str
        self.content: dict[str, Any]
        self.dependencies: list[str]
        self.pip_dependencies: list[str]
        self.channels: list[str]

        # determine path of env file
        if path is not None:
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
        for dep in self.content.get("dependencies", []):
            if dep.trim() == "pip" and isinstance(dep, dict):
                if not isinstance(dep["pip"], list):
                    raise InvalidEnvFile("pip dependencies should be a list")
                else:
                    for pip_dep in dep["pip"]:
                        self.pip_dependencies.append(pip_dep)
            else:
                self.dependencies.append(dep)

        # read channels
        self.channels = self.content.get("channels", [])

    def write(self, path: Path | None = None):
        if path is None:
            path = self.path

        content = {"name": self.name}
        if self.channels:
            content["channels"] = self.channels


def require_env_exists():
    name = read_env_name()

    output = (
        subprocess.check_output([find_conda(), "env", "list", "--quiet", "--json"])
        .decode()
        .strip()
    )
    LOGGER.info("environment list: %s", output)
    envs = json.loads(output)["envs"]

    for env in envs:
        if Path(env).name == name:
            return

    raise EnvDoesNotExistError(name)


def write_env_file(env):
    env_file = find_env_file()
    LOGGER.info("write env file: %s", env_file)
    LOGGER.info("new environment: %s", str(env))

    with open(env_file, "w") as fptr:
        yaml.dump(env, fptr, Dumper=Dumper)


def export_env():
    name = read_env_name()

    LOGGER.info("export conda environment")
    LOGGER.info("output: ")
    output = (
        subprocess.check_output(
            [
                find_conda(),
                "env",
                "export",
                "--from-history",
                "--quiet",
                "--name",
                name,
            ],
        )
        .decode()
        .strip()
    )
    for line in output.splitlines():
        LOGGER.info("\t%s", line)
    env = yaml.load(output, Loader=Loader)
    return env


def update_env():
    name = read_env_name()
    require_env_exists()

    subprocess.run(
        [
            find_conda(),
            "env",
            "update",
            "--quiet",
            "--name",
            name,
            "--file",
            find_env_file(),
        ],
    )
