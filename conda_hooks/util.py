from pathlib import Path
import subprocess
import re
import yaml

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

    output = (
        subprocess.check_output(["mamba", "env", "list", "--quiet"])
        .decode()
        .strip()
        .splitlines()
    )

    regex = re.compile("^" + name + r"\s+")
    environment_exists = False
    for line in output:
        if regex.match(line):
            environment_exists = True
            break

    if not environment_exists:
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
