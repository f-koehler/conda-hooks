from __future__ import annotations

import json
import logging
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

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


@lru_cache
def find_env_file(path: Path | None) -> Path:
    if path is not None:
        if path.exists():
            return path
        else:
            LOGGER.error("specified environment file does not exist: {path}")
            exit(1)
    for default_path in ENV_DEFAULT_PATHS:
        if default_path.exists():
            LOGGER.info("found env file: {default_path}")
            return default_path

    raise EnvFileNotFoundError()


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


@lru_cache
def read_env_name() -> str:
    env = read_env_file()
    if "name" not in env:
        raise InvalidEnvFile("environment name missing")
    LOGGER.info("found env name: %s", env["name"])

    return env["name"]


@lru_cache
def read_pip_dependencies():
    env = read_env_file()
    pip_dependencies = None
    for dep in env.get("dependencies", []):
        if isinstance(dep, dict) and ("pip" in dep):
            pip_dependencies = dep
            break

    if pip_dependencies:
        LOGGER.info("found pip dependencies:")
        for dep in pip_dependencies["pip"]:
            LOGGER.info("\t%s", dep)
    else:
        LOGGER.info("found no pip dependencies")

    return pip_dependencies


@lru_cache
def read_channels():
    env = read_env_file()
    return env.get("channels", [])


def read_env_file():
    env_file = find_env_file()
    LOGGER.info("read env file: %s", env_file)

    with open(env_file) as fptr:
        return yaml.load(fptr, Loader=Loader)


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
