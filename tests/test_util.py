import shutil
from pathlib import Path

import pytest

from conda_hooks import errors, util


@pytest.fixture
def data_directory(tmpdir: Path, request: pytest.FixtureRequest):
    path = Path(request.module.__file__).with_suffix("")

    if path.is_dir():
        shutil.copytree(path, tmpdir, dirs_exist_ok=True)

    return path


def test_find_conda_executable(data_directory: Path):
    with pytest.raises(errors.NoCondaExecutableError):
        util.find_conda_executable(data_directory / "no_exe")

    assert (
        util.find_conda_executable(data_directory / "only_conda")
        == data_directory / "only_conda" / "conda"
    )

    assert (
        util.find_conda_executable(data_directory / "mamba_conda")
        == data_directory / "mamba_conda" / "mamba"
    )
