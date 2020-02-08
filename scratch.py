from __future__ import annotations

import pathlib
import os.path as path


ROOT = "examples/complex/logs/filter_bounds"


if __name__ == "__main__":
    for i in range(31):
        full = path.join(ROOT, str(i) + ".txt")
        pathlib.Path(full).touch()
