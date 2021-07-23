import logging

from .util import EnvironmentFile, CondaHookError

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def main():
    try:
        env = EnvironmentFile()
        env.update_env()
    except CondaHookError as e:
        LOGGER.error(f"conda-hooks error: {e}")


if __name__ == "__main__":
    main()
