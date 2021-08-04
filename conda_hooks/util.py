from __future__ import annotations

import logging
import shutil
from pathlib import Path

from . import errors

LOGGER = logging.getLogger(__name__)
"""A logger to use throughout the module."""


def find_conda_executable(
    path: str | Path | None = None, allow_mamba: bool = True
) -> Path:
    """Find mamba/conda executable.

    This routine finds an executable to run conda commands. It prefers mamba since it
    is much faster for many operations. If mamba is not present in the PATH environment
    variable it will try to locate conda instead.

    Returns:
        Path of the mamba/conda executable.

    Raises:
        NoCondaExecutableError: If no mamba/conda executable was found.
    """
    if path is not None:
        path = str(path)

    if allow_mamba:
        result = shutil.which("mamba", path=path)
        if result:
            exe_path = Path(result).resolve()
            LOGGER.info(f"found mamba: {exe_path}")
            return exe_path

    LOGGER.warning("did not find mamba, try to find conda (which might be slower)")

    result = shutil.which("conda", path=path)
    if result:
        exe_path = Path(result).resolve()
        LOGGER.info(f"found conda: {exe_path}")
        return exe_path

    raise errors.NoCondaExecutableError()
