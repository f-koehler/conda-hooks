import os
from pathlib import Path

import pytest
from util import TestDir

from conda_hooks import environment, errors


def test_missing_file():
    with TestDir(__file__):
        with pytest.raises(errors.EnvFileNotFoundError):
            environment.EnvironmentFile("this_file_does_not_exist.yml")


def test_missing_name():
    with TestDir(__file__):
        with pytest.raises(errors.InvalidEnvFile):
            environment.EnvironmentFile("missing_name.yml")


def test_empty_env_file():
    with TestDir(__file__):
        env = environment.EnvironmentFile("empty.yml")
        assert env.name == "conda_hooks_empty"
        assert env.dependencies == []
        assert env.pip_dependencies == []
        assert env.channels == []


def test_default_path():
    with TestDir(__file__):
        env = environment.EnvironmentFile()
        assert env.name == "conda_hooks_default"
        assert env.path == Path("environment.yml")

        os.remove("environment.yml")
        with pytest.raises(errors.EnvFileNotFoundError):
            env = environment.EnvironmentFile()


def test_unsorted_deps():
    with TestDir(__file__):
        env = environment.EnvironmentFile("unsorted_deps.yml")
        assert env.name == "conda_hooks_unsorted_deps"
        assert env.dependencies == ["absl", "matplotlib", "numpy"]


def test_pip_deps():
    with TestDir(__file__):
        env = environment.EnvironmentFile("pip_deps.yml")
        assert env.name == "conda_hooks_pip_deps"
        assert env.dependencies == ["numpy", "pip"]
        assert env.pip_dependencies == ["matplotlib", "mypy"]

        with pytest.raises(errors.InvalidEnvFile):
            environment.EnvironmentFile("invalid_pip_deps.yml")


def test_channels():
    with TestDir(__file__):
        env = environment.EnvironmentFile("channels.yml")
        assert env.channels == ["nvidia", "pytorch", "conda-forge"]


def test_require_env_exists():
    with TestDir(__file__):
        env = environment.EnvironmentFile("non_existent_env.yml")
        with pytest.raises(errors.EnvDoesNotExistError):
            env.require_env_exists()


def test_write():
    with TestDir(__file__):
        # write file
        env = environment.EnvironmentFile("write.yml")
        env.write()

        # read file back
        env_new = environment.EnvironmentFile("write.yml")
        assert env.path == env_new.path
        assert env.name == env_new.name
        assert env.dependencies == env_new.dependencies
        assert env.pip_dependencies == env_new.pip_dependencies
        assert env.channels == env_new.channels


def test_create_remove():
    with TestDir(__file__):
        env = environment.EnvironmentFile("small.yml")
        env.remove()

        assert not env.exists()

        env.create()
        assert env.exists()
        env.create()

        env.remove()
        assert not env.exists()
        env.remove()
