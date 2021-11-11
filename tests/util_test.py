from pathlib import Path

import pytest
from util import TestDir

from conda_hooks import errors, util


def test_find_conda_executable():
    with TestDir(__file__):
        with pytest.raises(errors.NoCondaExecutableError):
            util.find_conda_executable("no_exe")

        path = str(util.find_conda_executable("only_conda"))
        expected_path = str((Path("only_conda") / "conda").resolve())
        assert path == expected_path

        path = str(util.find_conda_executable("mamba_conda", allow_mamba=True))
        expected_path = str((Path("mamba_conda") / "mamba").resolve())
        assert path == expected_path
