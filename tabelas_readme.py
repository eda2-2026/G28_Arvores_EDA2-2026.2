"""Atualiza as tabelas de resultados do README a partir do benchmark.

Roda com: python tabelas_readme.py   (depois de python comparacao.py)

As tabelas ficam no README entre marcadores:
    <!-- tabela:cronologico -->  ...  <!-- /tabela -->
Tudo entre eles é reescrito com os números de assets/ultimos_resultados.json,
com uma coluna por estrutura de ESTRUTURAS. O texto de análise fora das
tabelas não muda.
"""

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
README = RAIZ / "README.md"
ARQUIVO = RAIZ / "assets" / "ultimos_resultados.json"
N_DO_README = 8000  # os títulos das seções do README citam n = 8.000


def numero(valor, casas=0, unidade=""):
    """Formata no padrão brasileiro: 8.000 / 11,98 / 2.033,0 ms."""
    if casas == "auto":  # até 2 casas, sem zero sobrando (4.000,5 / 11,98)
        texto = f"{valor:,.2f}".rstrip("0").rstrip(".")
    else:
        texto = f"{valor:,.{casas}f}"
    texto = texto.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{texto} {unidade}".strip()


# (rótulo da linha, campo no JSON, formatação)
LINHAS_CADASTRO = [
    ("Altura", "altura", {}),
    ("Comparações por busca", "comparacoes_por_busca", {"casas": "auto"}),
    ("Rotações", "rotacoes_insercao", {}),
    ("Tempo de inserção", "tempo_insercao_ms", {"casas": 1, "unidade": "ms"}),
]
LINHAS_POR_TABELA = {
    "cronologico": LINHAS_CADASTRO,
    "aleatorio": LINHAS_CADASTRO,
    "cancelamentos": [
        ("Tempo de remoção", "tempo_remocao_ms", {"casas": 1, "unidade": "ms"}),
        ("Rotações na remoção", "rotacoes_remocao", {}),
        ("Altura depois", "altura_apos_remocao", {}),
    ],
    "base_real": [
        ("Altura", "altura", {}),
        ("Comparações por busca", "comparacoes_por_busca", {"casas": "auto"}),
        ("Tempo de inserção", "tempo_insercao_ms", {"casas": 1, "unidade": "ms"}),
        ("Remoção das 240 canceladas", "tempo_remocao_ms", {"casas": 1, "unidade": "ms"}),
    ],
}


def tabela(linhas_cenario, linhas_tabela):
    n_max = max(l["n"] for l in linhas_cenario)
    colunas = [l for l in linhas_cenario if l["n"] == n_max]
    saida = ["| | " + " | ".join(c["estrutura"] for c in colunas) + " |"]
    saida.append("|---" * (len(colunas) + 1) + "|")
    for rotulo, campo, formato in linhas_tabela:
        if not any(campo in c for c in colunas):
            continue  # campo que nenhuma estrutura mediu
        valores = [numero(c[campo], **formato) if campo in c else "-" for c in colunas]
        saida.append(f"| {rotulo} | " + " | ".join(valores) + " |")
    return "\n".join(saida)


def main():
    dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    if max(dados["tamanhos"]) != N_DO_README:
        sys.exit(
            f"O benchmark foi rodado até n = {max(dados['tamanhos'])}, mas o README fala em n = {N_DO_README}. "
            "Rode `python comparacao.py` sem argumentos antes de atualizar as tabelas."
        )
    texto = README.read_text(encoding="utf-8")
    faltando = []
    for cenario, linhas_tabela in LINHAS_POR_TABELA.items():
        padrao = re.compile(rf"(<!-- tabela:{cenario} -->\n).*?(\n<!-- /tabela -->)", re.S)
        if not padrao.search(texto):
            faltando.append(cenario)
            continue
        nova = tabela(dados["cenarios"][cenario], linhas_tabela)
        texto = padrao.sub(lambda m: m.group(1) + nova + m.group(2), texto)
        print(f"tabela '{cenario}' atualizada")
    if faltando:
        sys.exit(f"Marcadores não encontrados no README: {', '.join(faltando)}. Nada foi gravado.")
    with open(README, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(texto)
    print("Confira o texto da análise: ele cita números e não é atualizado por este script.")


if __name__ == "__main__":
    main()
