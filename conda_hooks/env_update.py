import logging

from . import util

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def main():
    try:
        util.update_env()
    except util.CondaHookError as e:
        LOGGER.error(f"conda-hooks error: {e}")


if __name__ == "__main__":
    main()
