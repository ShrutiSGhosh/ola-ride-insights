import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from pathlib import Path

py_path = Path("docs") / "EDA.py"
nb_path = Path("docs") / "EDA.ipynb"
# Read the python script (if missing, abort)
if not py_path.exists():
    raise SystemExit(f"Missing {py_path}")

script_text = py_path.read_text(encoding="utf-8")

nb = new_notebook()
# introductory markdown cell
nb.cells.append(new_markdown_cell("# EDA (recovered)\n\nThis notebook was automatically created from docs/EDA.py. Split the large code cell into multiple cells for step-by-step EDA."))
# Put the full script inside a single code cell (you can split this inside Jupyter)
nb.cells.append(new_code_cell(script_text))

nbformat.write(nb, str(nb_path))
print(f"Wrote notebook: {nb_path.resolve()}")
