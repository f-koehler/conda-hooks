import contextlib
import os
import shutil
import tempfile
from pathlib import Path


@contextlib.contextmanager
def TestDir(file: str):
    resource_dir = Path(file).with_suffix("").resolve()
    old_working_dir = Path.cwd().resolve()

    with tempfile.TemporaryDirectory() as tmpdir:
        working_dir = Path(tmpdir)
        if resource_dir.exists():
            shutil.copytree(resource_dir, working_dir, dirs_exist_ok=True)

        try:
            os.chdir(working_dir)
            yield
        finally:
            os.chdir(old_working_dir)
