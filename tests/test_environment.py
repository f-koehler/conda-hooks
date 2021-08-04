import os
import shutil
from pathlib import Path

import pytest

from conda_hooks import environment, errors


@pytest.fixture
def data_directory(tmpdir: Path, request: pytest.FixtureRequest):
    path = Path(request.module.__file__).with_suffix("")

    if path.is_dir():
        shutil.copytree(path, tmpdir, dirs_exist_ok=True)

    return path


def test_missing_file(data_directory: Path):
    with pytest.raises(errors.EnvFileNotFoundError):
        environment.EnvironmentFile(data_directory / "this_file_does_not_exist.yml")


def test_missing_name(data_directory: Path):
    with pytest.raises(errors.InvalidEnvFile):
        environment.EnvironmentFile(data_directory / "missing_name.yml")


def test_empty_env_file(data_directory: Path):
    env = environment.EnvironmentFile(data_directory / "empty.yml")
    assert env.name == "conda_hooks_empty"
    assert env.dependencies == []
    assert env.pip_dependencies == []
    assert env.channels == []


def test_default_path(data_directory: Path):
    wd = os.getcwd()
    os.chdir(data_directory)
    env = environment.EnvironmentFile()
    assert env.name == "conda_hooks_default"
    assert env.path == Path("environment.yml")
    os.chdir(wd)


def test_unsorted_deps(data_directory: Path):
    env = environment.EnvironmentFile(data_directory / "unsorted_deps.yml")
    assert env.name == "conda_hooks_unsorted_deps"
    assert env.dependencies == ["absl", "matplotlib", "numpy"]


def test_pip_deps(data_directory: Path):
    env = environment.EnvironmentFile(data_directory / "pip_deps.yml")
    assert env.name == "conda_hooks_pip_deps"
    assert env.dependencies == ["numpy", "pip"]
    assert env.pip_dependencies == ["matplotlib", "mypy"]


def test_channels(data_directory: Path):
    env = environment.EnvironmentFile(data_directory / "channels.yml")
    assert env.channels == ["nvidia", "pytorch", "conda-forge"]


def test_require_env_exists(data_directory: Path):
    env = environment.EnvironmentFile(data_directory / "non_existent_env.yml")
    with pytest.raises(errors.EnvDoesNotExistError):
        env.require_env_exists()


def test_write(data_directory: Path):
    # write file
    env = environment.EnvironmentFile(data_directory / "write.yml")
    env.write()

    # read file back
    env_new = environment.EnvironmentFile(data_directory / "write.yml")
    assert env.path == env_new.path
    assert env.name == env_new.name
    assert env.dependencies == env_new.dependencies
    assert env.pip_dependencies == env_new.pip_dependencies
    assert env.channels == env_new.channels


def test_create_remove(data_directory: Path):
    env = environment.EnvironmentFile(data_directory / "small.yml")
    env.remove()

    assert not env.exists()

    env.create()
    assert env.exists()
    env.create()

    env.remove()
    assert not env.exists()
    env.remove()
