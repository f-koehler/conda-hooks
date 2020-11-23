import subprocess
from pathlib import Path
import yaml
import re

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def main():
    if not Path("environment.yml").exists():
        print("environment.yml does not exist, skipping")
        exit(0)

    with open("environment.yml", "r") as fptr:
        name = yaml.load(fptr)["name"]

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

    output = (
        subprocess.check_output(["mamba", "env", "export", "--from-history", "--quiet"])
        .decode()
        .strip()
    )
    env = yaml.load(output)
    env["dependencies"] = sorted(env["dependencies"])

    with open("environment.yml", "w") as fptr:
        yaml.dump(env, fptr, Dumper=Dumper)


if __name__ == "__main__":
    main()
