"""Cenários de entrada do benchmark (seed 42, reproduzíveis).

Cada cenário devolve (insercoes, remocoes): a ordem em que as chaves são
inseridas e, depois, quais são removidas.

- cronologico:   consultas cadastradas em ordem de data (o caso comum numa
                 agenda, e o pior caso da BST).
- aleatorio:     as mesmas datas em ordem embaralhada (caso médio da BST).
- cancelamentos: cadastro em ordem de data e, depois, metade das consultas
                 cancelada em ordem aleatória (mede a remoção).
- base_real:     as consultas de dados/consultas_clinica.csv, na ordem do
                 arquivo. A chave é (data_hora, médico), para caber numa só
                 árvore. Tamanho fixo: 2.004.
"""

import random

from .models import carregar_consultas, gerar_horarios

SEMENTE = 42


def cronologico(n):
    return gerar_horarios(n), []


def aleatorio(n):
    chaves = gerar_horarios(n)
    random.Random(SEMENTE).shuffle(chaves)
    return chaves, []


def cancelamentos(n):
    chaves = gerar_horarios(n)
    remocoes = random.Random(SEMENTE).sample(chaves, n // 2)
    return chaves, remocoes


def base_real(n=None):
    consultas = carregar_consultas()
    chaves = [(c.data_hora, c.medico) for c in consultas]
    canceladas = [(c.data_hora, c.medico) for c in consultas if c.status == "cancelada"]
    return chaves, canceladas


CENARIOS = {
    "cronologico": cronologico,
    "aleatorio": aleatorio,
    "cancelamentos": cancelamentos,
    "base_real": base_real,
}
