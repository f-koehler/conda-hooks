from __future__ import annotations

import os
import subprocess
from pathlib import Path

from util import TestDir

from conda_hooks import env_store, environment, util


def test_get_env_files():
    with TestDir(__file__):
        parser = env_store.get_argument_parser()
        assert env_store.get_env_files(parser.parse_args([])) == [
            Path("environment.yml").resolve(),
        ]

        files = list(
            sorted(
                env_store.get_env_files(
                    parser.parse_args(["--glob", "glob/environment*.yml"]),
                ),
            ),
        )
        expected = list(
            sorted(
                Path("glob").resolve() / entry
                for entry in ["environment1.yml", "environment2.yml"]
            ),
        )
        assert files == expected

        files = list(
            sorted(
                env_store.get_env_files(
                    parser.parse_args(
                        ["--glob", "glob/environment*.yml", "--glob", "glob/env*.yaml"],
                    ),
                ),
            ),
        )
        expected = list(
            sorted(
                Path("glob").resolve() / entry
                for entry in ["env3.yaml", "environment1.yml", "environment2.yml"]
            ),
        )
        assert files == expected

        files = list(
            sorted(
                env_store.get_env_files(
                    parser.parse_args(
                        [
                            "--glob",
                            "glob/env*.yaml",
                            "glob/environment1.yml",
                            "glob/environment2.yml",
                        ],
                    ),
                ),
            ),
        )
        expected = list(
            sorted(
                Path("glob").resolve() / entry
                for entry in ["env3.yaml", "environment1.yml", "environment2.yml"]
            ),
        )
        assert files == expected


def test_main():
    with TestDir(__file__):
        stored_env = environment.EnvironmentFile()
        stored_env.create()

        env_store.main([])
        new_env = environment.EnvironmentFile()
        assert stored_env.name == new_env.name
        assert stored_env.env_file_path == new_env.env_file_path
        assert stored_env.channels == new_env.channels
        assert stored_env.dependencies == new_env.dependencies
        assert stored_env.pip_dependencies == new_env.pip_dependencies

        subprocess.run(
            [
                str(util.find_conda_executable()),
                "install",
                "-n",
                stored_env.name,
                "-q",
                "-y",
                "jinja2",
            ],
            check=True,
        )
        env_store.main([])
        new_env = environment.EnvironmentFile()
        assert stored_env.name == new_env.name
        assert stored_env.env_file_path == new_env.env_file_path
        assert stored_env.channels == new_env.channels
        assert stored_env.pip_dependencies == new_env.pip_dependencies

        new_deps = [
            dep for dep in new_env.dependencies if dep not in stored_env.dependencies
        ]
        assert new_deps == [
            "jinja2",
        ]

        stored_env.remove()
        os.remove("environment.yml")
        env_store.main([])
