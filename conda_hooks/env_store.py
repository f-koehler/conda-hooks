import logging

from .environment import EnvironmentFile
from .errors import CondaHookError

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def main():
    try:
        env = EnvironmentFile()

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
