import shutil
from pathlib import Path

import pytest

from conda_hooks import util


@pytest.fixture
def data_directory(tmpdir: Path, request: pytest.FixtureRequest):
    path = Path(request.module.__file__).with_suffix("")

    if path.is_dir():
        shutil.copytree(path, tmpdir, dirs_exist_ok=True)

    return path


def test_missing_name(data_directory: Path):
    with pytest.raises(util.InvalidEnvFile):
        util.EnvironmentFile(data_directory / "missing_name.yml")


def test_empty_env_file(data_directory: Path):
    env = util.EnvironmentFile(data_directory / "empty.yml")
    assert env.dependencies == []
    assert env.pip_dependencies == []
    assert env.channels == []


def test_unsorted_deps(data_directory: Path):
    env = util.EnvironmentFile(data_directory / "unsorted_deps.yml")
    assert env.dependencies == ["absl", "matplotlib", "numpy"]


def test_pip_deps(data_directory: Path):
    env = util.EnvironmentFile(data_directory / "pip_deps.yml")
    assert env.dependencies == ["numpy", "pip"]
    assert env.pip_dependencies == ["matplotlib", "mypy"]


def test_channels(data_directory: Path):
    env = util.EnvironmentFile(data_directory / "channels.yml")
    assert env.channels == ["nvidia", "pytorch", "conda-forge"]


# def test_create_remove(data_directory: Path):
#     env = util.EnvironmentFile(data_directory / "small.yml")
#     env.remove()

#     assert not env.exists()

#     env.create()
#     assert env.exists()

#     env.remove()
#     assert not env.exists()
