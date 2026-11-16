"""Benchmark das árvores na agenda da clínica.

Roda com: python comparacao.py              (tamanhos padrão)
          python comparacao.py 1000 5000    (tamanhos escolhidos)

Para cada cenário, estrutura e tamanho mede:
- tempo de inserção e de remoção (mediana de 3 execuções, em ms);
- altura final, rotações e média de comparações por busca.

Tempos dependem da máquina. Altura, rotações e comparações não: são sempre
as mesmas para a mesma entrada (seed 42).

Salva tudo em assets/ultimos_resultados.json (lido por plot_results.py).
"""

import json
import platform
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

from src.arvores import ESTRUTURAS
from src.cenarios import CENARIOS

TAMANHOS_PADRAO = [1000, 2000, 4000, 8000]
REPETICOES = 3
ARQUIVO_SAIDA = Path(__file__).resolve().parent / "assets" / "ultimos_resultados.json"


def medir(Arvore, insercoes, remocoes):
    """Executa uma rodada completa e devolve as medidas dela."""
    arvore = Arvore()
    inicio = time.perf_counter()
    for chave in insercoes:
        arvore.inserir(chave)
    tempo_insercao = (time.perf_counter() - inicio) * 1000

    resultado = {
        "tempo_insercao_ms": tempo_insercao,
        "altura": arvore.altura(),
        "rotacoes_insercao": arvore.rotacoes,
        "comparacoes_por_busca": arvore.comparacoes_medias_busca(insercoes),
    }
    if hasattr(arvore, "recoloracoes"):  # só a Rubro-Negra conta recolorações
        resultado["recoloracoes_insercao"] = arvore.recoloracoes

    if remocoes:
        rotacoes_antes = arvore.rotacoes
        recoloracoes_antes = getattr(arvore, "recoloracoes", 0)
        inicio = time.perf_counter()
        for chave in remocoes:
            arvore.remover(chave)
        resultado["tempo_remocao_ms"] = (time.perf_counter() - inicio) * 1000
        resultado["rotacoes_remocao"] = arvore.rotacoes - rotacoes_antes
        if hasattr(arvore, "recoloracoes"):
            resultado["recoloracoes_remocao"] = arvore.recoloracoes - recoloracoes_antes
        resultado["altura_apos_remocao"] = arvore.altura()

    arvore.validar()  # o benchmark só vale se a árvore terminou correta
    return resultado


def medir_com_repeticoes(Arvore, insercoes, remocoes):
    rodadas = [medir(Arvore, insercoes, remocoes) for _ in range(REPETICOES)]
    final = dict(rodadas[0])  # contagens são iguais em todas as rodadas
    for campo in ("tempo_insercao_ms", "tempo_remocao_ms"):
        if campo in final:
            final[campo] = round(statistics.median(r[campo] for r in rodadas), 3)
    final["comparacoes_por_busca"] = round(final["comparacoes_por_busca"], 3)
    return final


def main():
    tamanhos = [int(t) for t in sys.argv[1:]] or TAMANHOS_PADRAO
    resultados = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "maquina": f"{platform.system()} {platform.machine()}",
        "repeticoes": REPETICOES,
        "estruturas": [Arvore.nome for Arvore in ESTRUTURAS],
        "tamanhos": tamanhos,
        "cenarios": {},
    }

    for nome_cenario, gerar in CENARIOS.items():
        tamanhos_cenario = [None] if nome_cenario == "base_real" else tamanhos
        linhas = []
        for n in tamanhos_cenario:
            insercoes, remocoes = gerar(n)
            for Arvore in ESTRUTURAS:
                medida = medir_com_repeticoes(Arvore, insercoes, remocoes)
                medida.update(estrutura=Arvore.nome, n=len(insercoes))
                linhas.append(medida)
                imprimir(nome_cenario, medida)
        resultados["cenarios"][nome_cenario] = linhas

    ARQUIVO_SAIDA.parent.mkdir(exist_ok=True)
    ARQUIVO_SAIDA.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResultados salvos em {ARQUIVO_SAIDA}")


def imprimir(cenario, m):
    texto = (
        f"{cenario:<13} {m['estrutura']:<11} n={m['n']:>5} | altura {m['altura']:>5} | "
        f"busca {m['comparacoes_por_busca']:>8.2f} comp. | inserção {m['tempo_insercao_ms']:>9.1f} ms | "
        f"{m['rotacoes_insercao']:>5} rot."
    )
    if "tempo_remocao_ms" in m:
        texto += f" | remoção {m['tempo_remocao_ms']:>7.1f} ms, {m['rotacoes_remocao']:>5} rot."
    if "recoloracoes_insercao" in m:
        texto += f" | {m['recoloracoes_insercao']:>5} recolor."
    if "recoloracoes_remocao" in m:
        texto += f" | {m['recoloracoes_remocao']:>5} recolor. na remoção"
    print(texto)


if __name__ == "__main__":
    main()
