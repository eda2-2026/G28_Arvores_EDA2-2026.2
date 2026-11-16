"""Gera os gráficos a partir de assets/ultimos_resultados.json.

Roda com: python plot_results.py   (depois de python comparacao.py)
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # gera arquivos sem abrir janela
import matplotlib.pyplot as plt

PASTA = Path(__file__).resolve().parent / "assets"
ARQUIVO = PASTA / "ultimos_resultados.json"

# Uma cor fixa por estrutura em todos os gráficos.
CORES = {"BST": "#c0392b", "AVL": "#2471a3", "Rubro-Negra": "#7d3c98"}
MARCADORES = {"BST": "o", "AVL": "s", "Rubro-Negra": "^"}
NOMES_CENARIOS = {
    "cronologico": "Cadastro em ordem de data",
    "aleatorio": "Cadastro em ordem aleatória",
    "cancelamentos": "Cancelamento de metade das consultas",
}


def linhas_por_estrutura(linhas):
    grupos = {}
    for linha in linhas:
        grupos.setdefault(linha["estrutura"], []).append(linha)
    return grupos


def grafico_linhas(eixo, linhas, campo, titulo, rotulo_y, log=False):
    for estrutura, grupo in linhas_por_estrutura(linhas).items():
        eixo.plot(
            [l["n"] for l in grupo],
            [l[campo] for l in grupo],
            marker=MARCADORES.get(estrutura, "o"),
            color=CORES.get(estrutura),
            label=estrutura,
        )
    eixo.set_title(titulo)
    eixo.set_xlabel("número de consultas (n)")
    eixo.set_ylabel(rotulo_y)
    if log:
        eixo.set_yscale("log")
    eixo.grid(alpha=0.3)
    eixo.legend()


def salvar(figura, nome):
    figura.tight_layout()
    caminho = PASTA / nome
    figura.savefig(caminho, dpi=120)
    plt.close(figura)
    print(f"gerado {caminho.name}")


def main():
    dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    cen = dados["cenarios"]

    # 1. Altura: o gráfico que mostra a BST virando lista
    figura, eixos = plt.subplots(1, 2, figsize=(12, 4.5))
    grafico_linhas(eixos[0], cen["cronologico"], "altura", NOMES_CENARIOS["cronologico"], "altura (níveis, escala log)", log=True)
    grafico_linhas(eixos[1], cen["aleatorio"], "altura", NOMES_CENARIOS["aleatorio"], "altura (níveis)")
    eixos[1].set_ylim(bottom=0)
    figura.suptitle("Altura final da árvore")
    salvar(figura, "altura.png")

    # 2. Comparações por busca (custo de "esse horário está livre?")
    figura, eixos = plt.subplots(1, 2, figsize=(12, 4.5))
    for eixo, nome in zip(eixos, ("cronologico", "aleatorio")):
        grafico_linhas(eixo, cen[nome], "comparacoes_por_busca", NOMES_CENARIOS[nome], "comparações (escala log)", log=True)
    figura.suptitle("Média de comparações por busca")
    salvar(figura, "comparacoes_busca.png")

    # 3. Tempo de inserção
    figura, eixos = plt.subplots(1, 2, figsize=(12, 4.5))
    for eixo, nome in zip(eixos, ("cronologico", "aleatorio")):
        grafico_linhas(eixo, cen[nome], "tempo_insercao_ms", NOMES_CENARIOS[nome], "tempo (ms, escala log)", log=True)
    figura.suptitle("Tempo para cadastrar todas as consultas")
    salvar(figura, "tempo_insercao.png")

    # 4. Rotações na inserção (o preço do balanceamento)
    figura, eixos = plt.subplots(1, 2, figsize=(12, 4.5))
    for eixo, nome in zip(eixos, ("cronologico", "aleatorio")):
        grafico_linhas(eixo, cen[nome], "rotacoes_insercao", NOMES_CENARIOS[nome], "rotações")
    figura.suptitle("Rotações feitas durante o cadastro")
    salvar(figura, "rotacoes.png")

    # 5. Remoção (cancelamentos)
    figura, eixos = plt.subplots(1, 2, figsize=(12, 4.5))
    grafico_linhas(eixos[0], cen["cancelamentos"], "tempo_remocao_ms", "Tempo para cancelar n/2 consultas", "tempo (ms, escala log)", log=True)
    grafico_linhas(eixos[1], cen["cancelamentos"], "rotacoes_remocao", "Rotações nos cancelamentos", "rotações")
    figura.suptitle(NOMES_CENARIOS["cancelamentos"])
    salvar(figura, "remocao.png")

    # 6. Base real da clínica
    linhas = cen["base_real"]
    nomes = [l["estrutura"] for l in linhas]
    cores = [CORES.get(n) for n in nomes]
    figura, eixos = plt.subplots(1, 3, figsize=(13, 4.2))
    for eixo, campo, titulo in zip(
        eixos,
        ("altura", "comparacoes_por_busca", "tempo_insercao_ms"),
        ("Altura", "Comparações por busca", "Tempo de cadastro (ms)"),
    ):
        barras = eixo.bar(nomes, [l[campo] for l in linhas], color=cores)
        eixo.bar_label(barras, fmt="%.1f" if campo != "altura" else "%d")
        eixo.set_title(titulo)
        eixo.set_yscale("log")
        eixo.grid(axis="y", alpha=0.3)
    figura.suptitle(f"Base real da clínica ({linhas[0]['n']} consultas do CSV, em ordem de data)")
    salvar(figura, "base_real.png")


if __name__ == "__main__":
    main()
