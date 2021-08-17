import os
import subprocess

from util import TestDir

from conda_hooks import env_store, environment, util


def test_main():
    with TestDir(__file__):
        stored_env = environment.EnvironmentFile()
        stored_env.create()

        env_store.main([])
        new_env = environment.EnvironmentFile()
        assert stored_env.name == new_env.name
        assert stored_env.path == new_env.path
        assert stored_env.channels == new_env.channels
        assert stored_env.dependencies == new_env.dependencies
        assert stored_env.pip_dependencies == new_env.pip_dependencies

        subprocess.run(
            [
                str(util.find_conda_executable(allow_mamba=False)),
                "install",
                "-n",
                stored_env.name,
                "-q",
                "-y",
                "flake8",
            ]
        )
        env_store.main([])
        new_env = environment.EnvironmentFile()
        assert stored_env.name == new_env.name
        assert stored_env.path == new_env.path
        assert stored_env.channels == new_env.channels
        assert stored_env.pip_dependencies == new_env.pip_dependencies

        new_deps = [
            dep for dep in new_env.dependencies if dep not in stored_env.dependencies
        ]
        assert new_deps == [
            "flake8",
        ]

        stored_env.remove()
        os.remove("environment.yml")
        env_store.main([])
