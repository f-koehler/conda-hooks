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
            shutil.rmtree(working_dir)

        shutil.copytree(resource_dir, working_dir)

        try:
            os.chdir(working_dir)
            yield
        finally:
            os.chdir(old_working_dir)
