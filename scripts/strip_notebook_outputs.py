from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"


def iter_notebooks(targets: list[str]) -> Iterable[Path]:
    if targets:
        for item in targets:
            p = Path(item)
            if p.is_dir():
                yield from sorted(p.rglob("*.ipynb"))
            elif p.suffix == ".ipynb" and p.exists():
                yield p
        return

    yield from sorted(DEFAULT_NOTEBOOK_DIR.rglob("*.ipynb"))


def strip_notebook(path: Path) -> bool:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    metadata = notebook.get("metadata", {})
    if isinstance(metadata, dict) and "widgets" in metadata:
        del metadata["widgets"]
        changed = True

    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue

        if cell.get("outputs"):
            cell["outputs"] = []
            changed = True

        if cell.get("execution_count") is not None:
            cell["execution_count"] = None
            changed = True

    if changed:
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    return changed


def has_output_or_exec_count(path: Path) -> bool:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    metadata = notebook.get("metadata", {})
    if isinstance(metadata, dict) and "widgets" in metadata:
        return True

    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        if cell.get("outputs"):
            return True
        if cell.get("execution_count") is not None:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove outputs/execution_count de notebooks para evitar vazamento de dados.",
    )
    parser.add_argument("paths", nargs="*", help="Arquivos ou pastas alvo.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Apenas verifica; retorna erro se encontrar notebooks com saída.",
    )
    args = parser.parse_args()

    notebooks = list(iter_notebooks(args.paths))
    if not notebooks:
        print("Nenhum notebook encontrado.")
        return 0

    changed: list[Path] = []
    dirty: list[Path] = []

    if args.check:
        for notebook in notebooks:
            if has_output_or_exec_count(notebook):
                dirty.append(notebook)
        if dirty:
            print("Notebooks com outputs/execution_count detectados:")
            for p in dirty:
                print(f"- {p}")
            return 1
        print("OK: notebooks sem outputs/execution_count.")
        return 0

    for notebook in notebooks:
        if strip_notebook(notebook):
            changed.append(notebook)

    print(f"Notebooks processados: {len(notebooks)}")
    print(f"Notebooks alterados: {len(changed)}")
    for p in changed:
        print(f"- {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
