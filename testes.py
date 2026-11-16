"""Testes de corretude das árvores.

Roda com: python testes.py

validar() confere as regras da árvore (na maioria dos testes, depois de cada
operação). No fim de cada teste, o conteúdo da árvore é comparado com um
dicionário (o resultado esperado).
"""

import math
import random
from datetime import datetime, timedelta

from src.agenda import Agenda
from src.arvores import AVL, ESTRUTURAS, BST
from src.arvores.rubro_negra import RubroNegra
from src.models import CAMINHO_BASE, Consulta, carregar_consultas, gerar_horarios

SEMENTE = 42


# ----------------------------------------------------------------------
# Auxiliares
# ----------------------------------------------------------------------
def conferir_com_modelo(arvore, modelo):
    """A árvore precisa ter exatamente as chaves e valores do dicionário."""
    arvore.validar()
    assert len(arvore) == len(modelo)
    assert list(arvore.em_ordem()) == sorted(modelo.items())


def teste(funcao):
    TESTES.append(funcao)
    return funcao


TESTES = []


# ----------------------------------------------------------------------
# Testes comuns a todas as árvores
# ----------------------------------------------------------------------
@teste
def arvore_vazia():
    for Arvore in ESTRUTURAS:
        arvore = Arvore()
        assert len(arvore) == 0 and arvore.altura() == 0
        assert arvore.buscar(1) is None and arvore.minimo() is None
        assert arvore.a_partir_de(1) is None and arvore.intervalo(0, 10) == []
        assert arvore.remover(1) is False
        arvore.validar()


@teste
def insercao_cronologica():
    horarios = gerar_horarios(500)
    for Arvore in ESTRUTURAS:
        arvore, modelo = Arvore(), {}
        for i, horario in enumerate(horarios):
            assert arvore.inserir(horario, f"paciente {i}")
            modelo[horario] = f"paciente {i}"
            arvore.validar()
        conferir_com_modelo(arvore, modelo)


@teste
def insercao_aleatoria_e_busca():
    horarios = gerar_horarios(1000)
    random.Random(SEMENTE).shuffle(horarios)
    for Arvore in ESTRUTURAS:
        arvore, modelo = Arvore(), {}
        for horario in horarios:
            arvore.inserir(horario, horario.isoformat())
            modelo[horario] = horario.isoformat()
        conferir_com_modelo(arvore, modelo)
        for horario in horarios[:200]:
            assert arvore.buscar(horario) == horario.isoformat()
            assert horario in arvore
        assert arvore.buscar(horarios[0] + timedelta(minutes=1)) is None


@teste
def horario_ocupado_nao_sobrescreve():
    horario = gerar_horarios(1)[0]
    for Arvore in ESTRUTURAS:
        arvore = Arvore()
        assert arvore.inserir(horario, "Ana")
        assert not arvore.inserir(horario, "Bruno")  # mesmo médico, mesmo horário
        assert arvore.buscar(horario) == "Ana" and len(arvore) == 1


@teste
def remocao_misturada():
    """Insere e remove em ordem aleatória, conferindo tudo a cada passo."""
    rng = random.Random(SEMENTE)
    horarios = gerar_horarios(400)
    for Arvore in ESTRUTURAS:
        arvore, modelo = Arvore(), {}
        for _ in range(3000):
            horario = rng.choice(horarios)
            if rng.random() < 0.6:
                assert arvore.inserir(horario, 1) == (horario not in modelo)
                modelo.setdefault(horario, 1)
            else:
                assert arvore.remover(horario) == (horario in modelo)
                modelo.pop(horario, None)
            arvore.validar()
        conferir_com_modelo(arvore, modelo)
        for horario in list(modelo):  # esvazia tudo
            assert arvore.remover(horario)
        conferir_com_modelo(arvore, {})


@teste
def remocao_dos_tres_casos():
    """Folha, nó com um filho e nó com dois filhos."""
    for Arvore in ESTRUTURAS:
        arvore = Arvore()
        for chave in (50, 30, 70, 20, 40, 60, 80, 65):
            arvore.inserir(chave)
        assert arvore.remover(20)  # folha
        assert arvore.remover(60)  # um filho (65)
        assert arvore.remover(50)  # dois filhos (a raiz)
        arvore.validar()
        assert arvore.chaves() == [30, 40, 65, 70, 80]


@teste
def sucessor_e_intervalo():
    horarios = gerar_horarios(160)  # 10 dias úteis
    ocupados = horarios[::3]
    for Arvore in ESTRUTURAS:
        arvore = Arvore()
        for horario in ocupados:
            arvore.inserir(horario)
        # próxima consulta a partir de cada horário
        for horario in horarios:
            esperado = next((h for h in ocupados if h >= horario), None)
            assert arvore.a_partir_de(horario) == esperado
        # agenda de um dia
        dia = horarios[40].date()
        inicio, fim = horarios[40].replace(hour=0), horarios[40].replace(hour=23, minute=59)
        esperado = [h for h in ocupados if h.date() == dia]
        assert [chave for chave, _ in arvore.intervalo(inicio, fim)] == esperado
        # limites inclusivos: início e fim caindo em cima de consultas existentes
        a, b = ocupados[5], ocupados[9]
        assert [chave for chave, _ in arvore.intervalo(a, b)] == ocupados[5:10]
        assert [chave for chave, _ in arvore.intervalo(a, a)] == [a]
        assert arvore.intervalo(b, a) == []  # intervalo invertido
        assert arvore.minimo() == ocupados[0] and arvore.maximo() == ocupados[-1]


@teste
def desenho():
    for Arvore in ESTRUTURAS:
        arvore = Arvore()
        assert arvore.desenhar() == "(árvore vazia)"
        for chave in (2, 1, 3):
            arvore.inserir(chave)
        linhas = arvore.desenhar().splitlines()
        assert len(linhas) == 3
        assert "3" in linhas[0] and linhas[1].startswith("2") and "1" in linhas[2]


@teste
def base_real_da_clinica():
    """Carrega o CSV e monta uma árvore por médico, como a agenda vai fazer."""
    consultas = carregar_consultas(CAMINHO_BASE)
    assert len(consultas) == 2004
    por_medico = {}
    for consulta in consultas:
        por_medico.setdefault(consulta.medico, []).append(consulta)
    assert len(por_medico) == 3
    for Arvore in ESTRUTURAS:
        for medico, lista in por_medico.items():
            arvore = Arvore()
            for consulta in lista:
                assert arvore.inserir(consulta.data_hora, consulta), "horário duplicado na base"
            arvore.validar()
            assert len(arvore) == len(lista)
            primeira = min(lista, key=lambda c: c.data_hora)
            assert arvore.buscar(primeira.data_hora) is primeira


# ----------------------------------------------------------------------
# Testes específicos da BST
# ----------------------------------------------------------------------
@teste
def bst_degenera_com_datas_em_ordem():
    """O pior caso que motiva o trabalho: datas em ordem viram uma lista."""
    n = 8000
    bst = BST()
    for horario in gerar_horarios(n):
        bst.inserir(horario)
    assert bst.altura() == n
    assert bst.rotacoes == 0
    bst.validar()  # validar e altura são iterativos: não estouram a recursão
    # buscar a última consulta percorre a árvore inteira
    bst.zerar_contadores()
    bst.buscar(bst.maximo())
    assert bst.comparacoes == n


@teste
def bst_aleatoria_fica_baixa():
    horarios = gerar_horarios(8000)
    random.Random(SEMENTE).shuffle(horarios)
    bst = BST()
    for horario in horarios:
        bst.inserir(horario)
    # altura esperada de BST aleatória é cerca de 4,3 * ln(n), bem longe de n
    assert bst.altura() < 60


# ----------------------------------------------------------------------
# Testes específicos da AVL
# ----------------------------------------------------------------------
def limite_altura_avl(n):
    """Altura máxima teórica de uma AVL com n nós: cerca de 1,44 * log2(n + 2)."""
    return 1.4405 * math.log2(n + 2) - 0.3277


@teste
def avl_quatro_casos_de_rotacao():
    """Cada caso clássico, com 3 chaves, termina com a mesma árvore equilibrada."""
    casos = {
        "esquerda-esquerda": (30, 20, 10),
        "direita-direita": (10, 20, 30),
        "esquerda-direita": (30, 10, 20),
        "direita-esquerda": (10, 30, 20),
    }
    for nome, chaves in casos.items():
        avl = AVL()
        for chave in chaves:
            avl.inserir(chave)
        avl.validar()
        assert avl.raiz.chave == 20, nome
        assert avl.raiz.esq.chave == 10 and avl.raiz.dir.chave == 30, nome
        simples = nome in ("esquerda-esquerda", "direita-direita")
        assert avl.rotacoes == (1 if simples else 2), nome


@teste
def avl_fica_baixa_com_datas_em_ordem():
    """Mesmo pior caso da BST: aqui a árvore continua com altura O(log n)."""
    n = 8000
    avl = AVL()
    horarios = gerar_horarios(n)
    for horario in horarios:
        avl.inserir(horario)
    avl.validar()
    assert avl.altura() <= limite_altura_avl(n)
    assert avl.altura() == 13  # 8.000 em ordem: árvore quase perfeita (log2 8000 = 12,97)
    assert avl.rotacoes > 0
    assert avl.comparacoes_medias_busca(horarios) < 14


@teste
def avl_remocao_rebalanceia():
    """Remover metade das consultas mantém a AVL dentro do limite de altura."""
    horarios = gerar_horarios(4000)
    avl = AVL()
    for horario in horarios:
        avl.inserir(horario)
    rotacoes_insercao = avl.rotacoes
    for horario in horarios[: len(horarios) // 2]:  # cancela as mais antigas
        assert avl.remover(horario)
    avl.validar()
    assert len(avl) == 2000
    assert avl.altura() <= limite_altura_avl(2000)
    assert avl.rotacoes > rotacoes_insercao  # a remoção também precisou rotacionar


@teste
def avl_verbose_mostra_rotacoes():
    """O modo verbose (usado na demonstração) imprime cada rotação."""
    import contextlib
    import io

    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        avl = AVL(verbose=True)
        for chave in (10, 20, 30):
            avl.inserir(chave)
    texto = saida.getvalue()
    assert "direita-direita" in texto and "rotação à esquerda em 10" in texto


# ----------------------------------------------------------------------
# Testes específicos da Rubro-Negra
# ----------------------------------------------------------------------
@teste
def rubro_negra_quatro_casos_de_insercao():
    """Os casos internos e externos espelhados corrigem a raiz e a ordem."""
    casos = {
        "esquerda-esquerda": ((30, 20, 10), 1),
        "esquerda-direita": ((30, 10, 20), 2),
        "direita-direita": ((10, 20, 30), 1),
        "direita-esquerda": ((10, 30, 20), 2),
    }
    for nome, (chaves, rotacoes) in casos.items():
        arvore = RubroNegra()
        for chave in chaves:
            assert arvore.inserir(chave)
        arvore.validar()
        assert arvore.raiz.chave == 20, nome
        assert arvore.raiz.esq.chave == 10 and arvore.raiz.dir.chave == 30, nome
        assert arvore.rotacoes == rotacoes, nome


@teste
def rubro_negra_recolore_com_tio_vermelho():
    arvore = RubroNegra()
    for chave in (10, 5, 15, 1):
        arvore.inserir(chave)
    arvore.validar()
    assert arvore.raiz.cor == "preto"
    assert arvore.raiz.esq.cor == arvore.raiz.dir.cor == "preto"
    assert arvore.raiz.esq.esq.cor == "vermelho"
    assert arvore.recoloracoes > 0
    arvore.zerar_contadores()
    assert arvore.recoloracoes == arvore.rotacoes == arvore.comparacoes == 0


@teste
def rubro_negra_conta_cor_do_sucessor_na_remocao():
    arvore = RubroNegra()
    for chave in (2, 1, 3):
        arvore.inserir(chave)
    antes = arvore.recoloracoes
    assert arvore.remover(2)
    arvore.validar()
    assert arvore.raiz.chave == 3 and arvore.raiz.cor == "preto"
    assert arvore.recoloracoes == antes + 1


@teste
def rubro_negra_fica_baixa_com_datas_em_ordem():
    """Mesmo com entrada cronológica, a altura fica limitada por 2 log2(n+1)."""
    horarios = gerar_horarios(8000)
    arvore = RubroNegra()
    for horario in horarios:
        assert arvore.inserir(horario)
    arvore.validar()
    assert arvore.altura() <= 2 * math.ceil(math.log2(len(arvore) + 1))
    assert arvore.comparacoes_medias_busca(horarios) < 2 * math.ceil(math.log2(len(arvore) + 1))
    assert arvore.rotacoes > 0 and arvore.recoloracoes > 0


@teste
def rubro_negra_operacoes_misturadas():
    """Confere invariantes e conteúdo após cada inserção ou remoção aleatória."""
    rng = random.Random(SEMENTE)
    arvore, modelo = RubroNegra(), {}
    for passo in range(3000):
        chave = rng.randrange(400)
        if rng.random() < 0.6:
            inserida = chave not in modelo
            assert arvore.inserir(chave, passo) == inserida
            if inserida:
                modelo[chave] = passo
        else:
            removida = chave in modelo
            assert arvore.remover(chave) == removida
            modelo.pop(chave, None)
        arvore.validar()
        assert list(arvore.em_ordem()) == sorted(modelo.items())


@teste
def rubro_negra_verbose_mostra_caso_e_rotacao():
    import contextlib
    import io

    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        arvore = RubroNegra(verbose=True)
        for chave in (30, 20, 10):
            arvore.inserir(chave)
    texto = saida.getvalue()
    assert "esquerda-esquerda" in texto and "rotação à direita" in texto


# ----------------------------------------------------------------------
# Testes da agenda da clínica
# ----------------------------------------------------------------------
@teste
def agenda_operacoes_do_dia_a_dia():
    for Arvore in ESTRUTURAS:
        agenda = Agenda(Arvore)
        medico = "Dra. Teste"
        seg_8h = datetime(2026, 11, 16, 8, 0)
        seg_8h30 = datetime(2026, 11, 16, 8, 30)
        consulta = Consulta(1, seg_8h, medico, "Ana", "consulta", "agendada")

        assert agenda.horario_livre(medico, seg_8h)
        assert agenda.agendar(consulta)
        assert not agenda.horario_livre(medico, seg_8h)
        assert not agenda.agendar(Consulta(2, seg_8h, medico, "Bruno", "consulta", "agendada"))
        # outro médico pode usar o mesmo horário
        assert agenda.agendar(Consulta(3, seg_8h, "Dr. Outro", "Caio", "exame", "agendada"))
        # fora do atendimento: domingo, horário quebrado, almoço
        for fora in (datetime(2026, 11, 22, 9), datetime(2026, 11, 16, 8, 15), datetime(2026, 11, 16, 12)):
            assert not agenda.horario_livre(medico, fora)
            assert not agenda.agendar(Consulta(4, fora, medico, "Davi", "consulta", "agendada"))

        assert agenda.proximo_horario_livre(medico, seg_8h) == seg_8h30
        assert agenda.proxima_consulta(medico, datetime(2026, 11, 16, 7)) is consulta
        assert agenda.proxima_consulta(medico, seg_8h30) is None

        assert agenda.remarcar(medico, seg_8h, seg_8h30)
        assert agenda.horario_livre(medico, seg_8h) and consulta.data_hora == seg_8h30
        assert not agenda.remarcar(medico, seg_8h, seg_8h30)  # não há consulta às 8h

        # remarcar para horário ocupado ou inválido não pode perder a consulta
        assert agenda.agendar(Consulta(5, seg_8h, medico, "Eva", "retorno", "agendada"))
        for invalido in (seg_8h, datetime(2026, 11, 22, 9)):
            assert not agenda.remarcar(medico, seg_8h30, invalido)
            assert agenda.arvore(medico).buscar(seg_8h30) is consulta and consulta.status == "agendada"
        assert agenda.cancelar(medico, seg_8h30) is consulta and consulta.status == "cancelada"
        assert agenda.cancelar(medico, seg_8h30) is None
        for arvore in agenda.arvores.values():
            arvore.validar()


@teste
def agenda_da_base_real():
    consultas = carregar_consultas(CAMINHO_BASE)
    agendadas = [c for c in consultas if c.status == "agendada"]
    for Arvore in ESTRUTURAS:
        agenda = Agenda.da_base(Arvore)
        assert agenda.total_consultas() == len(agendadas)
        medico = "Dra. Marina Souza"
        dia = datetime(2026, 11, 18)
        esperado = sorted(
            (c for c in agendadas if c.medico == medico and c.data_hora.date() == dia.date()),
            key=lambda c: c.data_hora,
        )
        assert agenda.agenda_do_dia(medico, dia) == esperado
        semana = agenda.agenda_da_semana(medico, dia)
        assert all(datetime(2026, 11, 16) <= c.data_hora < datetime(2026, 11, 23) for c in semana)
        assert len(semana) == sum(
            1 for c in agendadas if c.medico == medico and datetime(2026, 11, 16) <= c.data_hora < datetime(2026, 11, 23)
        )


# ----------------------------------------------------------------------
def main():
    for funcao in TESTES:
        funcao()
        print(f"ok  {funcao.__name__}")
    nomes = ", ".join(Arvore.nome for Arvore in ESTRUTURAS)
    print(f"\nTodos os testes passaram. ({len(TESTES)} testes; estruturas: {nomes})")


if __name__ == "__main__":
    main()
