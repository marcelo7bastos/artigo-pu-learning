from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "dados" / "dados_processados"


def _read_processed_or_skip(filename: str, columns: list[str]) -> pd.DataFrame:
    path = PROCESSED_DIR / filename
    if not path.exists():
        pytest.skip(f"Arquivo processado ausente: {path}")
    return pd.read_parquet(path, columns=columns, engine="pyarrow")


@pytest.mark.contracts
def test_demografia_contract():
    cols = [
        "ibge",
        "cpf_agricultor",
        "id_familia",
        "idade_2025",
        "A",
        "AC",
        "B",
        "V",
        "Desconhecido",
    ]
    df = _read_processed_or_skip("df_caf_demografia.parquet", cols)

    assert df["cpf_agricultor"].notna().all()
    assert df["id_familia"].notna().all()
    assert df["cpf_agricultor"].nunique(dropna=False) == len(df)
    assert df["ibge"].astype("string").str.len().eq(7).all()
    assert df["idade_2025"].between(0, 120).all()
    assert (df[["A", "AC", "B", "V", "Desconhecido"]].sum(axis=1) == 1).all()


@pytest.mark.contracts
def test_produtiva_territorio_contract():
    cols = [
        "id_familia",
        "lat_imovel_principal",
        "lon_imovel_principal",
        "n_imoveis_total",
        "n_imoveis_ha",
        "n_imoveis_m2",
        "n_imoveis_m3",
        "st_geo_valida",
    ]
    df = _read_processed_or_skip("df_caf_ufpa_produtiva_territorio.parquet", cols)

    assert df["id_familia"].notna().all()
    assert df["id_familia"].nunique(dropna=False) == len(df)
    assert set(df["st_geo_valida"].dropna().astype(int).unique()).issubset({0, 1})

    counts = df[["n_imoveis_total", "n_imoveis_ha", "n_imoveis_m2", "n_imoveis_m3"]].dropna()
    assert (
        counts["n_imoveis_total"]
        == counts["n_imoveis_ha"] + counts["n_imoveis_m2"] + counts["n_imoveis_m3"]
    ).all()

    lat_ok = df["lat_imovel_principal"].isna() | df["lat_imovel_principal"].between(-33.75, 5.27)
    lon_ok = df["lon_imovel_principal"].isna() | df["lon_imovel_principal"].between(-73.99, -28.84)
    assert (lat_ok & lon_ok).all()


@pytest.mark.contracts
def test_renda_atividade_contract():
    cols = [
        "id_familia",
        "renda_total_estimada",
        "renda_top1_produto_estimada",
        "share_top1_produto_estimada",
        "n_tipos_renda",
        "n_produtos",
        "st_possui_renda",
    ]
    df = _read_processed_or_skip("df_caf_ufpa_renda_atividade.parquet", cols)

    assert df["id_familia"].notna().all()
    assert df["id_familia"].nunique(dropna=False) == len(df)
    assert (df["n_tipos_renda"] >= 0).all()
    assert (df["n_produtos"] >= 0).all()
    assert df["share_top1_produto_estimada"].between(0, 1).all()
    assert (df["renda_top1_produto_estimada"] <= df["renda_total_estimada"]).all()

    expected_flag = (df["renda_total_estimada"] > 0).astype("int8")
    assert (df["st_possui_renda"].astype("int8") == expected_flag).all()


@pytest.mark.contracts
def test_consolidado_contract():
    consolidated_cols = [
        "cpf_agricultor",
        "id_familia",
        "st_tem_ufpa",
        "st_tem_renda_atividade",
    ]
    demo_cols = ["cpf_agricultor"]

    consolidated = _read_processed_or_skip(
        "df_caf_demografia_ufpa_consolidado.parquet",
        consolidated_cols,
    )
    demografia = _read_processed_or_skip("df_caf_demografia.parquet", demo_cols)

    assert len(consolidated) == len(demografia)
    assert consolidated["cpf_agricultor"].nunique(dropna=False) == len(consolidated)
    assert set(consolidated["st_tem_ufpa"].dropna().astype(int).unique()).issubset({0, 1})
    assert set(consolidated["st_tem_renda_atividade"].dropna().astype(int).unique()).issubset({0, 1})


@pytest.mark.contracts
def test_pronaf_rotulo_pu_contract():
    cols = [
        "cpf_agricultor",
        "n_ops_pronaf_5a",
        "valor_total_pronaf_5a",
        "ano_ult_op_pronaf",
        "s",
    ]
    df = _read_processed_or_skip("pronaf_rotulo_pu_5anos.parquet", cols)

    assert df["cpf_agricultor"].notna().all()
    assert df["cpf_agricultor"].astype("string").str.len().eq(11).all()
    assert df["cpf_agricultor"].nunique(dropna=False) == len(df)

    assert df["n_ops_pronaf_5a"].notna().all()
    assert (df["n_ops_pronaf_5a"] >= 1).all()
    assert df["valor_total_pronaf_5a"].notna().all()
    assert df["ano_ult_op_pronaf"].between(2021, 2025).all()

    assert set(df["s"].dropna().astype(int).unique()) == {1}
