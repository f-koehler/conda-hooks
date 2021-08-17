from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Sequence

from .environment import ENV_DEFAULT_PATHS, EnvironmentFile
from .errors import CondaHookError, EnvFileNotFoundError, NoEnvFileError, NotAFileError

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--glob", type=str, nargs="*", default=[])
    parser.add_argument("files", type=Path, nargs="*", default=[])
    args = parser.parse_args(argv)

    try:
        files: list[Path] = []
        for glob in args.glob:
            files += Path.cwd().glob(glob)
        for file in args.files:
            if not file.exists():
                raise EnvFileNotFoundError(file)
            if not file.is_file():
                raise NotAFileError(file)
            files.append(file)

        if not files:
            files = [
                file for file in ENV_DEFAULT_PATHS if file.exists() and file.is_file()
            ]

        if not files:
            raise NoEnvFileError()

        for file in files:
            env = EnvironmentFile(file)

            if env.exists():
                for dep in env.get_installed_dependencies():
                    if dep not in env.dependencies:
                        env.dependencies.append(dep)

            env.dependencies.sort()
            env.write()
    except CondaHookError as e:
        LOGGER.error(f"conda-hooks error: {e}")


if __name__ == "__main__":
    main()
