from pathlib import Path
import subprocess
import re
import yaml
import json
import logging
from functools import lru_cache
import shutil

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


@lru_cache
def find_mamba():
    path = shutil.which("mamba")
    if not path:
        LOGGER.error("failed to find mamba")
        exit(0)

    LOGGER.info("found mamba: %s", str(Path(path).resolve()))
    return path


@lru_cache
def find_env_file():
    path = Path("environment.yml")
    if not path.exists():
        LOGGER.error("failed to find env file")
        exit(0)

    LOGGER.info("found env file: %s", "environment.yml")
    return str(path)


def require_env_exists():
    name = read_env_name()

    output = (
        subprocess.check_output(
            [find_mamba(), "env", "list", "--quiet", "--json"], shell=True
        )
        .decode()
        .strip()
    )
    LOGGER.info("environment list: %s", output)
    envs = json.loads(output)["envs"]

    for env in envs:
        if Path(env).name == name:
            return

    print("the environment has not yet been created, skipping")
    exit(0)


@lru_cache
def read_env_name():
    env = read_env_file()
    if "name" not in env:
        LOGGER.error("env file does not include a name field")
        exit(0)
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


def read_env_file():
    LOGGER.info("read env file")
    env_file = find_env_file()

    with open(env_file, "r") as fptr:
        return yaml.load(fptr, Loader=Loader)


def write_env_file(env):
    LOGGER.info("write env file")
    env_file = find_env_file()

    with open(env_file, "w") as fptr:
        yaml.dump(env, fptr, Dumper=Dumper)


def export_env():
    name = read_env_name()

    LOGGER.info("export conda environment")
    LOGGER.info("output: ")
    output = (
        subprocess.check_output(
            [
                find_mamba(),
                "env",
                "export",
                "--from-history",
                "--quiet",
                "--name",
                name,
            ],
            shell=True,
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
            find_mamba(),
            "env",
            "update",
            "--quiet",
            "--name",
            name,
            "--file",
            find_env_file(),
        ],
        shell=True,
    )
