"""Run both workshop notebooks from top to bottom in a scratch folder.

The notebooks write a few CSV files, so they run in a temporary copy of the
repository. The script stops with an error if any cell fails or if any
reference solution does not print the expected result.

Run:  python tools/run_notebooks.py
"""
import shutil
import sys
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copytree(ROOT / "data", tmp / "data")
        (tmp / "notebooks").mkdir()
        for path in sorted((ROOT / "notebooks").glob("NOKTA_AI_Workshop_*.ipynb")):
            if ".executed" in path.name:
                continue
            nb = nbformat.read(path, as_version=4)
            client = NotebookClient(nb, timeout=900, kernel_name="python3",
                                    resources={"metadata": {"path": str(tmp / "notebooks")}})
            try:
                client.execute()
            except Exception as exc:          # report and continue with the next notebook
                print(f"FAIL {path.name}: {str(exc)[:500]}")
                failures += 1
                continue
            checks = [o.get("text", "") for c in nb.cells if c.cell_type == "code"
                      for o in c.get("outputs", []) if "✓" in o.get("text", "")]
            print(f"OK   {path.name}: {len(checks)} reference solutions confirmed")
            if len(checks) < 6:
                failures += 1
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
