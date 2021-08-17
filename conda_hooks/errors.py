from __future__ import annotations

from pathlib import Path


class CondaHookError(Exception):
    pass


class NoCondaExecutableError(CondaHookError):
    def __init__(self):
        super().__init__("failed to find mamba/conda")


class NoEnvFileError(CondaHookError):
    def __init__(self):
        super().__init__("failed to find any env file")


class EnvFileNotFoundError(CondaHookError):
    def __init__(self, path: str | Path):
        super().__init__(f"env file does not exist: {path}")


class NotAFileError(CondaHookError):
    def __init__(self, path: str | Path):
        super().__init__(f"not a file: {path}")


class InvalidEnvFile(CondaHookError):
    def __init__(self, message: str):
        super().__init__(f"invalid env file: {message}")


class EnvDoesNotExistError(CondaHookError):
    def __init__(self, name: str):
        super().__init__(f"environment does not exist: {name}")
