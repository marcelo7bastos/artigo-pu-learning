import json
import os
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
ACTIVE_NOTEBOOKS = [
    NOTEBOOKS_DIR / "01_preparacao_demografia.ipynb",
    NOTEBOOKS_DIR / "02_preparacao_produtiva_territorio.ipynb",
    NOTEBOOKS_DIR / "03_preparacao_renda_atividade.ipynb",
    NOTEBOOKS_DIR / "04_join_demografia_ufpa.ipynb",
    NOTEBOOKS_DIR / "05_preparacao_pronaf_rotulo_pu.ipynb",
    NOTEBOOKS_DIR / "06_join_demografia_ufpa_pronaf_rotulo_pu.ipynb",
]


def _iter_code_cells(notebook_path: Path):
    nb = json.loads(notebook_path.read_text(encoding="utf-8"))
    for idx, cell in enumerate(nb["cells"]):
        if cell.get("cell_type") == "code":
            yield idx, "".join(cell.get("source", []))


@pytest.mark.smoke
def test_active_notebooks_exist():
    missing = [str(p) for p in ACTIVE_NOTEBOOKS if not p.exists()]
    assert not missing, f"Notebooks ativos ausentes: {missing}"


@pytest.mark.smoke
def test_active_notebooks_code_cells_compile():
    for notebook in ACTIVE_NOTEBOOKS:
        for idx, source in _iter_code_cells(notebook):
            compile(source, f"{notebook}::cell_{idx}", "exec")


@pytest.mark.smoke
@pytest.mark.slow
def test_active_notebooks_execute_smoke():
    if os.getenv("RUN_NOTEBOOK_SMOKE") != "1":
        pytest.skip("Defina RUN_NOTEBOOK_SMOKE=1 para executar os notebooks ponta a ponta.")

    cwd = Path.cwd()
    os.chdir(PROJECT_ROOT)
    try:
        for notebook in ACTIVE_NOTEBOOKS:
            namespace = {}
            for idx, source in _iter_code_cells(notebook):
                exec(compile(source, f"{notebook}::cell_{idx}", "exec"), namespace)
    finally:
        os.chdir(cwd)
