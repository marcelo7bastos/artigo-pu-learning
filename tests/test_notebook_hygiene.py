import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"


def test_notebooks_do_not_store_outputs_or_execution_count():
    notebooks = sorted(NOTEBOOKS_DIR.rglob("*.ipynb"))
    assert notebooks, "Nenhum notebook encontrado para validacao."

    dirty = []
    for notebook_path in notebooks:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))

        if "widgets" in notebook.get("metadata", {}):
            dirty.append(f"{notebook_path} -> metadata.widgets presente")
            continue

        for idx, cell in enumerate(notebook.get("cells", [])):
            if cell.get("cell_type") != "code":
                continue
            if cell.get("outputs"):
                dirty.append(f"{notebook_path} -> cell {idx} possui outputs")
            if cell.get("execution_count") is not None:
                dirty.append(f"{notebook_path} -> cell {idx} possui execution_count")

    assert not dirty, "Notebooks com saida embutida:\n" + "\n".join(dirty)
