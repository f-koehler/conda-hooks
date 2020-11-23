from pathlib import Path
import subprocess
import re
import yaml
import json

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def require_env_file():
    if not Path("environment.yml").exists():
        print("environment.yml does not exist, skipping")
        exit(0)


def require_env_exists():
    name = read_env_name()

    envs = json.loads(
        subprocess.check_output(["mamba", "env", "list", "--quiet", "--json"])
        .decode()
        .strip()
    )["envs"]

    for env in envs:
        if Path(env).name == name:
            return

    print("the environment has not yet been created, skipping")
    exit(0)


def read_env_file():
    require_env_file()

    with open("environment.yml", "r") as fptr:
        return yaml.load(fptr, Loader=Loader)


def read_env_name():
    env = read_env_file()
    if "name" not in env:
        print("environment.yml does not include a name field")
        exit(0)
    return env["name"]


def read_pip_dependencies():
    env = read_env_file()
    pip_dependencies = []
    for dep in env.get("dependencies", []):
        if isinstance(dep, dict) and ("pip" in dep):
            pip_dependencies = dep
            break
    return pip_dependencies


def write_env_file(env):
    with open("environment.yml", "w") as fptr:
        yaml.dump(env, fptr, Dumper=Dumper)


def export_env():
    name = read_env_name()

    output = (
        subprocess.check_output(
            ["mamba", "env", "export", "--from-history", "--quiet", "--name", name]
        )
        .decode()
        .strip()
    )
    env = yaml.load(output, Loader=Loader)
    print("exported environment:")
    print(env)
    return env


def update_env():
    name = read_env_name()
    require_env_exists()

    subprocess.run(
        [
            "mamba",
            "env",
            "update",
            "--quiet",
            "--name",
            name,
            "--file",
            "environment.yml",
        ]
    )
