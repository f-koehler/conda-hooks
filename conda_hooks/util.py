import json
import logging
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import yaml
from yaml import CDumper as Dumper
from yaml import CLoader as Loader

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


@lru_cache
def find_conda():
    path = shutil.which("mamba")
    if path:
        LOGGER.info("found mamba: %s", str(Path(path).resolve()))
        return path

    LOGGER.warn("did not find mamba, try to find conda (which might be slower)")

    path = shutil.which("conda")
    if not path:
        LOGGER.error("failed to find conda")
        exit(0)

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
        subprocess.check_output([find_conda(), "env", "list", "--quiet", "--json"])
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
