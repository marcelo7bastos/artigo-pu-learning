# PU Learning no acesso ao Pronaf

[Edição publicada pela Enap](https://repositorio.enap.gov.br/handle/1/10139) · 2026 · p. 216–231.

Esta edição pública reúne os notebooks do estudo, o código auxiliar, as dependências e os testes. Os microdados do CAF e as bases e saídas individualizadas ficam fora desta distribuição.

Repositório de apoio a artigo científico sobre **Positive-Unlabeled (PU) Learning aplicado ao acesso ao crédito do PRONAF**, com preparação de bases administrativas do CAF, rotulagem observada via SICOR e comparação de estratégias de modelagem para priorização operacional.

## Sobre o projeto

No PRONAF, a ausência de acesso observado ao crédito não equivale necessariamente à ausência de propensão, elegibilidade ou perfil compatível. O que se observa diretamente é o rótulo de seleção `S`: agricultores com contratação observada recebem `S=1`; agricultores sem contratação observada recebem `S=0`.

O problema é formulado como **Positive-Unlabeled Learning** porque `S=0` é um grupo **unlabeled**: ele mistura negativos reais e positivos ocultos. A classe latente `Y`, associada ao perfil ou à propensão real de acesso, não é observada diretamente.

O artigo trabalha sob a hipótese **SCAR** (*Selected Completely at Random*) para a trilha clássica de PU Learning. Nessa hipótese, a probabilidade de um positivo real aparecer como rotulado é representada por uma constante `c = P(S=1 | Y=1)`.

## Dados, LGPD e disponibilidade

Este repositório contém código, notebooks e estrutura de pipeline. Ele **não deve ser interpretado como distribuição pública dos microdados** usados no estudo.

| Fonte | Uso no projeto | Disponibilidade |
| --- | --- | --- |
| CAF - Cadastro Nacional da Agricultura Familiar, referência 31/12/2025 | Atributos explicativos `X` em nível de indivíduo e família | Microdados individualizados são restritos por conterem dados pessoais. Acesso depende de autorização do MDA e deve observar a LGPD. |
| SICOR - Sistema de Operações do Crédito Rural e do Proagro, BCB, PRONAF 2021-2025 | Marcação de contratação observada (`S=1`) | Dados públicos disponíveis em https://www.bcb.gov.br/estabilidadefinanceira/tabelas-credito-rural-proagro |
| Agregados públicos CAF/DAP por município/UF, MDA | Apenas contexto e consulta agregada; **não** alimentam o pipeline nem reproduzem a modelagem | Dados públicos disponíveis em https://www.gov.br/mda/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/cadastro-nacional-da-agricultura-familiar/transparencia |

A preparação das bases do CAF, a base analítica cruzada CAF x SICOR e todos os modelos (trilhas A, B e C) dependem dos microdados individualizados do CAF, que exigem acesso autorizado. **Não é possível reproduzir essas etapas apenas com dados públicos.** Com os dados públicos do SICOR é possível reproduzir somente partes descritivas (por exemplo, a evolução do PRONAF); os agregados públicos do CAF/DAP servem apenas como contexto/consulta, não como insumo dos notebooks.

## Estrutura do repositório

Estrutura observada na raiz do projeto:

| Caminho | Descrição |
| --- | --- |
| `.githooks/` | Hooks locais, incluindo validação de higiene de notebooks. |
| `dados/dados_brutos/` | Local esperado para arquivos originais. No fluxo analítico, esses dados são tratados como entrada e não devem ser versionados. |
| `dados/dados_processados/` | Local esperado para bases intermediárias e finais. |
| `dados/dados_processados/outputs_pu/` | Artefatos das trilhas de modelagem, rankings, manifestos e métricas. |
| `dados/dados_processados/outputs_artigo/` | Tabelas e figuras consolidadas para o artigo. |
| `notebooks/` | Notebooks ativos do pipeline. |
| `scripts/` | Scripts utilitários, incluindo limpeza de outputs de notebooks. |
| `src/` | Utilitários Python, incluindo metadados CAF. |
| `tests/` | Testes de contratos de dados, smoke de notebooks e higiene. |
| `.python-version` | Versão local de Python: `3.12.4`. |
| `pyproject.toml` | Definição do ambiente e dependências via `uv`. |
| `uv.lock` | Lockfile do ambiente. |
| `README.md` | Este documento. |
| `LICENSE` | Licença MIT, aplicável ao código deste repositório. |

## Pipeline e notebooks ativos

A unidade de análise do estudo é o indivíduo (`cpf_agricultor`). Variáveis familiares são associadas por `id_familia`. A integração usa o CAF como referência, com *left join*, e o rótulo `S` vem da contratação observada no SICOR/PRONAF.

| Ordem | Notebook | Função | Entradas principais | Saídas principais |
| --- | --- | --- | --- | --- |
| 1 | `notebooks/01_preparacao_demografia.ipynb` | Prepara atributos demográficos em nível pessoa, padroniza identificadores, datas, idade e tipos. | `dados/dados_brutos/a_tcc_v2_pessoa_demografia_compilado.parquet` | `dados/dados_processados/df_caf_demografia.parquet` |
| 2 | `notebooks/02_preparacao_produtiva_territorio.ipynb` | Prepara variáveis produtivas e territoriais da UFPA em nível família. | Base bruta de produtiva/território, configurável por `PRODUTIVA_TERRITORIO_PATH` | `dados/dados_processados/df_caf_ufpa_produtiva_territorio.parquet` |
| 3 | `notebooks/03_preparacao_renda_atividade.ipynb` | Prepara variáveis de renda e atividade em nível família. | Base bruta de renda/atividade, configurável por `RENDA_ATIVIDADE_PATH` | `dados/dados_processados/df_caf_ufpa_renda_atividade.parquet` |
| 4 | `notebooks/04_join_demografia_ufpa.ipynb` | Integra demografia, UFPA produtiva/território e renda/atividade, replicando atributos familiares no nível pessoa. | `df_caf_demografia.parquet`, `df_caf_ufpa_produtiva_territorio.parquet`, `df_caf_ufpa_renda_atividade.parquet` | `dados/dados_processados/df_caf_demografia_ufpa_consolidado.parquet` |
| 5 | `notebooks/05_preparacao_pronaf_rotulo_pu.ipynb` | Prepara o rótulo PU a partir do PRONAF/SICOR, filtrando janela 2021-2025 e agregando por CPF. | `dados/dados_brutos/pronaf.parquet` | `dados/dados_processados/pronaf_rotulo_pu_5anos.parquet` |
| 6 | `notebooks/06_join_demografia_ufpa_pronaf_rotulo_pu.ipynb` | Faz o *left join* entre CAF consolidado e rótulo PRONAF, criando a base analítica com `s`. | `df_caf_demografia_ufpa_consolidado.parquet`, `pronaf_rotulo_pu_5anos.parquet` | `dados/dados_processados/df_caf_demografia_ufpa_pronaf_rotulo_pu.parquet` |
| 7 | `notebooks/12_avaliacao_higiene_features.ipynb` | Avalia tipos, missing, baixa variância, correlação, redundância e relação das features com `s`. | `df_caf_demografia_ufpa_pronaf_rotulo_pu.parquet` | Diagnósticos em notebook. |
| 8 | `notebooks/20_trilha_A_proxy_supervisionado_s.ipynb` | Trilha A: baseline supervisionado sobre `S`; compara HistGradientBoosting e XGBoost, com vencedor `A3`. | `df_caf_demografia_ufpa_pronaf_rotulo_pu.parquet` | `trilhaA_*`, incluindo scores, ranking Top 100k, métricas, modelo, SHAP e manifesto em `outputs_pu/`. |
| 9 | `notebooks/21_trilha_B_pu_classico.ipynb` | Trilha B: PU clássico sob SCAR com Elkan-Noto; compara B1, B2 e calibração B3. | `df_caf_demografia_ufpa_pronaf_rotulo_pu.parquet` | `trilhaB_*`, incluindo `trilhaB_comparacao_interna.parquet`, `trilhaB_artifacts_manifest.parquet`, scores, ranking, modelo e interpretabilidade. |
| 10 | `notebooks/22_trilha_C_nnpu.ipynb` | Trilha C: nnPU com MLP em PyTorch, prior principal e sensibilidade de prior. | `df_caf_demografia_ufpa_pronaf_rotulo_pu.parquet` | `trilhaC_*`, incluindo scores, ranking, métricas, histórico, sensibilidade, calibração, SHAP e modelo `.pt`. |
| 11 | `notebooks/90_tabelas_graficos_artigo.ipynb` | Consolida tabelas e gráficos para o artigo, incluindo evolução do PRONAF, AUC, recall e sobreposição Top 100k. | `pronaf.parquet`, artefatos em `outputs_pu/` | `outputs_artigo/tabela_auc_todas_as_trilhas.*`, `tabela_recall_todas_as_trilhas.*`, `tabela_sobreposicao_top100k_*`, `pronaf_evolucao_2015_2025.png`. |
| 12 | `notebooks/91_scoring_universo_trilhaB_b2_refit.ipynb` | Refit do B2 no universo e scoring completo para análises substantivas sobre `S=0`. | `df_caf_demografia_ufpa_pronaf_rotulo_pu.parquet`, `trilhaB_artifacts_manifest.parquet`, `trilhaB_best_model_pipeline.pkl` | `trilhaB_b2_scores_all*`, `trilhaB_b2_scores_s0*`, rankings Top/Bottom 100k e 1%, `trilhaB_b2_scores_all_analysis_ready.parquet`, manifesto de scoring. |
| 13 | `notebooks/92_resultados.ipynb` | Analisa os recortes de alta e baixa propensão estimada sem acesso observado, incluindo UF, papel familiar e sexo. | `trilhaB_b2_scores_all_analysis_ready.parquet` | Tabelas exibidas no notebook para interpretação substantiva. |
| 14 | `notebooks/99_comparacao_modelos.ipynb` | Recalcula comparação alternativa A-E no teste e salva tabela consolidada. | Scores em `outputs_pu/` | `outputs_pu/comparacao_modelos_A_E.parquet` e `.csv`. |

### O que roda com dados públicos e o que exige acesso autorizado

| Parte do fluxo | Pode ser reproduzida só com dados públicos? | Observação |
| --- | --- | --- |
| Preparação do SICOR/PRONAF público e análises agregadas de evolução | Parcialmente | Exige obter e transformar os dados públicos do BCB para o formato `dados/dados_brutos/pronaf.parquet`. |
| Uso de agregados públicos CAF/DAP | Não | Servem apenas para contexto/consulta agregada; não são insumo dos notebooks nem reproduzem a modelagem. |
| Preparação demográfica/produtiva/renda do CAF | Não | Exige os microdados individualizados do CAF, com acesso autorizado. |
| Base cruzada CAF x SICOR e modelos A/B/C | Não | Exige a base analítica individualizada e as chaves de integração. |
| Rankings Top/Bottom 100 mil em `S=0` | Não | Dependem do scoring individualizado do universo CAF. |

## Metodologia em resumo

| Elemento | Descrição |
| --- | --- |
| Unidade de análise | Indivíduo (`cpf_agricultor`). |
| Chave familiar | `id_familia`; atributos familiares são replicados para o nível pessoa quando integrados. |
| Alvo observado | `S=1` indica contratação observada no PRONAF; `S=0` indica ausência de contratação observada, não inelegibilidade. |
| Classe latente | `Y` representa perfil/propensão real e não é observada diretamente. |
| Split | Aproximadamente 80/10/10 para treino, validação e teste, com bloqueio por `id_familia` via `GroupShuffleSplit`. |
| Trilha A | Baseline supervisionado sobre `S`; vencedor `A3` = XGBoost. |
| Trilha B | Elkan-Noto sob SCAR; melhor modelo bruto `B2` = Elkan-Noto + XGBoostClassifier. |
| Trilha C | nnPU com rede MLP em PyTorch; execução principal `C1`. |
| Métricas | `AUC_S`, `Recall@{1,5,10}%` e `Precision@k`, sempre calculadas sobre `S` observado. |
| `hold_out_ratio` | `0.10` na execução principal; grade de sensibilidade de `0.05` a `0.20`. |
| `c` estimado | Aproximadamente `0.48`; avaliação B2: `0.4842`; refit do universo de scoring: `0.4836`. |
| Prior nnPU | `pi = 0.73` na execução principal; grade `0.65`, `0.70`, `0.73`, `0.75`. |
| Semente | `seed = 42`. |

A constante `c` é interpretada como taxa de cobertura efetiva dos positivos sob SCAR. Neste estudo, `c` próximo de `0.48` sugere que cerca de 48% dos positivos latentes apareceriam como rotulados no mecanismo observado, sob as hipóteses do método.

## Resultados principais

A fonte oficial das métricas do artigo é:

```text
dados/dados_processados/outputs_artigo/tabela_auc_todas_as_trilhas.parquet
```

Tabela principal de AUC de teste:

| Trilha | Componente | Modelo | AUC_S teste | Fonte |
| --- | --- | --- | ---: | --- |
| Trilha A | A3 | XGBoost supervisionado sobre `S` | 0.844 | `trilhaA_metricas_resumo.parquet` |
| Trilha B | B2 | Elkan-Noto + XGBoostClassifier | 0.825 | `trilhaB_comparacao_interna.parquet` |
| Trilha C | C1 | nnPU MLP (PyTorch) | 0.710 | `trilhaC_metrics_summary.parquet` |

As análises substantivas de Top/Bottom 100 mil foram feitas sobre agricultores com `S=0`, usando o ranking do **B2**. O manifesto de scoring registra `best_raw_model_code = B2`, `score_oficial = score_pu_b2_raw` e ordenação por `score_pu_b2_raw` decrescente.

Resultados de sobreposição Top 100k:

| Comparação | Interseção | Percentual sobre Top 100k | Jaccard |
| --- | ---: | ---: | ---: |
| Baseline supervisionado x PU clássico (Elkan-Noto/B2) | 80.769 | 80,8% | 0,677 |
| Baseline supervisionado x nnPU | 44.253 | 44,3% | 0,284 |
| PU clássico (Elkan-Noto/B2) x nnPU | 47.889 | 47,9% | 0,315 |

O arquivo `dados/dados_processados/outputs_pu/comparacao_modelos_A_E.parquet` existe, mas é um **corte alternativo** de comparação A-E. Ele não contém o B2 como linha da Trilha B e não deve ser usado como fonte da tabela principal do artigo.

## Como reproduzir

### Pré-requisitos

- Python `3.12.4` ou outra versão `3.12.x` compatível com `pyproject.toml`.
- `uv`.
- Acesso aos dados necessários, conforme a seção de dados e LGPD.

### Instalação do ambiente

```powershell
uv sync
```

Opcionalmente, ative o ambiente virtual local:

```powershell
.\.venv\Scripts\Activate.ps1
```

Dependências centrais declaradas no `pyproject.toml`:

| Pacote | Uso principal |
| --- | --- |
| `pandas`, `numpy`, `pyarrow` | Manipulação tabular e arquivos Parquet. |
| `scikit-learn` | Split por grupos, modelos, métricas e calibração. |
| `xgboost` | Classificador de Gradient Boosting usado nas trilhas supervisionadas e no B2. |
| `pulearn` | Implementação de Elkan-Noto para PU Learning clássico. |
| `torch` | Modelo nnPU em PyTorch. |
| `shap` | Interpretabilidade dos modelos. |
| `matplotlib` | Gráficos para o artigo. |
| `jupyterlab`, `ipykernel` | Execução dos notebooks. |
| `pytest` | Testes e validações automatizadas. |

### Organização esperada dos dados

Os notebooks esperam os arquivos em caminhos como:

```text
dados/dados_brutos/
dados/dados_processados/
dados/dados_processados/outputs_pu/
dados/dados_processados/outputs_artigo/
```

Entradas restritas do CAF devem ser colocadas localmente em `dados/dados_brutos/`, conforme nomes esperados pelos notebooks, mas não devem ser versionadas. O mesmo vale para bases processadas com microdados individualizados.

### Execução sugerida

Para reproduzir o fluxo completo com dados autorizados:

1. Executar os notebooks de preparação `01` a `06`.
2. Executar o diagnóstico `12`.
3. Executar as trilhas de modelagem `20`, `21` e `22`.
4. Executar `90` para consolidar tabelas e gráficos do artigo.
5. Executar `91` para refit/scoring do B2 no universo e criação dos recortes Top/Bottom.
6. Executar `92` para análises substantivas.
7. Usar `99` apenas quando o objetivo for reproduzir o corte alternativo `comparacao_modelos_A_E`.

Validações recomendadas:

```powershell
uv run python scripts/strip_notebook_outputs.py --check
uv run pytest -q
```

Smoke de notebooks, quando aplicável:

```powershell
$env:RUN_NOTEBOOK_SMOKE="1"
uv run pytest -q tests/test_notebook_smoke.py -m "smoke and slow"
Remove-Item Env:RUN_NOTEBOOK_SMOKE
```

## Reprodutibilidade e limitações

- `Y` não é observado. As métricas avaliam separação em relação a `S`, não desempenho direto em relação ao desfecho latente.
- `S=0` não significa inelegibilidade, ausência de perfil produtivo ou ausência de demanda por crédito.
- A hipótese SCAR é uma simplificação necessária para o Elkan-Noto; se a seleção dos positivos depender sistematicamente de `X`, a interpretação de `c` e dos scores deve ser cautelosa.
- A vinculação CAF x SICOR pode ter perdas. O contexto do projeto registra 574.741 CPFs do PRONAF não localizados no CAF, possivelmente por uso anterior da DAP.
- Os rankings Top/Bottom 100 mil são ferramentas operacionais de priorização e diagnóstico, não estimativas causais.
- A reprodução exata depende de acesso autorizado aos microdados CAF e à base individualizada integrada.

## Qualidade e higiene de notebooks

O repositório inclui validações para evitar versionamento de outputs embutidos em notebooks:

```powershell
uv run python scripts/strip_notebook_outputs.py --check
```

O hook local em `.githooks/pre-commit` bloqueia commits com notebooks contendo outputs ou contadores de execução. Os testes relevantes estão em:

| Arquivo | Finalidade |
| --- | --- |
| `tests/test_notebook_hygiene.py` | Higiene de notebooks. |
| `tests/test_notebook_smoke.py` | Smoke tests estruturais/de execução controlada. |
| `tests/test_data_contracts.py` | Contratos mínimos de dados. |

## Uso de inteligência artificial generativa

Na elaboração do artigo associado a este repositório, foram utilizadas ferramentas de inteligência artificial generativa (NotebookLM, Overleaf AI, Codex, ChatGPT e Claude) como apoio ao levantamento da bibliografia, à elaboração e à revisão de códigos, à formatação do manuscrito e à revisão da redação. Todo o conteúdo gerado com o auxílio dessas ferramentas foi submetido à revisão e ao julgamento crítico do autor. A concepção do problema, as decisões metodológicas, a execução e a validação das análises e a interpretação dos resultados permanecem sob responsabilidade integral do autor; as ferramentas não se qualificam como autoras. A declaração oficial consta no artigo.

## Como citar

BASTOS, Marcelo Cabreira. Estimativa de propensão e exclusão no crédito rural: uma abordagem de positive-unlabeled learning e gradient boosting com dados do PRONAF e CAF. In: DE TONI, Jackson Silvano; DORNELES, Rachel Pereira (org.). **Análise de dados e IA a serviço da inovação em gestão pública**. Brasília, DF: Enap, 2026. p. 216–231. Disponível em: [https://repositorio.enap.gov.br/handle/1/10139](https://repositorio.enap.gov.br/handle/1/10139). Acesso em: 24 nov. 2026.

## Licença e termos de uso dos dados

O código deste repositório é distribuído sob a licença **MIT** (ver arquivo [`LICENSE`](LICENSE)). A licença cobre apenas o código; os dados possuem restrições próprias, descritas abaixo.

Os dados possuem restrições próprias:

- Microdados CAF e bases individualizadas integradas CAF x SICOR: acesso restrito, sujeito à autorização institucional e à LGPD.
- SICOR/PRONAF público: observar os termos e a forma de disponibilização do Banco Central do Brasil.
- Agregados CAF/DAP públicos: observar os termos de disponibilização do MDA.

## Autor e contato

- Autor: Marcelo Cabreira Bastos.
- Orientador: Hélio Bonfim de Macêdo Filho.
- Contato: não informado neste repositório.
