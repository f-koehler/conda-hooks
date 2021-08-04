from pathlib import Path

import pytest
from util import TestDir

from conda_hooks import errors, util


def test_find_conda_executable():
    with TestDir(__file__):
        with pytest.raises(errors.NoCondaExecutableError):
            util.find_conda_executable("no_exe")

        assert (
            util.find_conda_executable("only_conda")
            == (Path("only_conda") / "conda").resolve()
        )

        assert (
            util.find_conda_executable("mamba_conda")
            == (Path("mamba_conda") / "mamba").resolve()
        )
