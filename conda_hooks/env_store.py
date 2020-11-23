from . import util


def main():
    pip_dependencies = util.read_pip_dependencies()

    util.require_env_exists()

    env = util.read_env_file()

    env["dependencies"] = sorted(env["dependencies"])
    if pip_dependencies:
        env["dependencies"].append(pip_dependencies)

    del env["prefix"]

    util.write_env_file(env)


if __name__ == "__main__":
    main()
