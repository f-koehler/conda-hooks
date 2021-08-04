class CondaHookError(Exception):
    pass


class NoCondaExecutableError(CondaHookError):
    def __init__(self):
        super().__init__("failed to find mamba/conda")


class EnvFileNotFoundError(CondaHookError):
    def __init__(self):
        super().__init__("failed to find env file")


class InvalidEnvFile(CondaHookError):
    def __init__(self, message: str):
        super().__init__(f"invalid env file: {message}")


class EnvDoesNotExistError(CondaHookError):
    def __init__(self, name: str):
        super().__init__(f"environment does not exist: {name}")
