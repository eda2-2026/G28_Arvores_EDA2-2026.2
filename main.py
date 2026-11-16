"""Demonstração passo a passo das árvores na agenda da clínica.

Roda com: python main.py

Parte 1: a BST recebendo consultas em ordem cronológica vira uma lista.
Parte 2: as árvores balanceadas recebendo as mesmas consultas (rotações aparecem).
Parte 3: cancelamentos (remoção com rebalanceamento).
Parte 4: a base real da clínica (dados/consultas_clinica.csv) em cada árvore.
Parte 5: a agenda funcionando: horário livre, agendar, cancelar, remarcar...
"""

from datetime import datetime

from src.agenda import Agenda
from src.arvores import ESTRUTURAS, BST
from src.models import Consulta, gerar_horarios

LARGURA = 72


def titulo(texto):
    print("\n" + "=" * LARGURA)
    print(texto)
    print("=" * LARGURA)


def subtitulo(texto):
    print(f"\n--- {texto} ---")


def resumo(arvore):
    return f"{arvore.nome}: {len(arvore)} consultas, altura {arvore.altura()}, {arvore.rotacoes} rotações"


# ----------------------------------------------------------------------
def parte_1_bst_degenera(horarios):
    titulo("PARTE 1 - BST com consultas cadastradas em ordem cronológica")
    print("Cada nova consulta é mais tarde que todas as anteriores,")
    print("então ela sempre vai para a DIREITA. A árvore vira uma lista.")
    bst = BST()
    for horario in horarios:
        bst.inserir(horario)
    print()
    print(bst.desenhar())
    print(f"\n{resumo(bst)}")
    print(f"Altura = número de consultas ({len(bst)}): buscar a última custa {len(bst)} comparações.")


def parte_2_balanceadas(horarios):
    titulo("PARTE 2 - As mesmas consultas nas árvores balanceadas")
    for Arvore in ESTRUTURAS:
        if Arvore is BST:
            continue
        subtitulo(f"{Arvore.nome}: inserindo em ordem, rotação por rotação")
        arvore = Arvore(verbose=True)
        for horario in horarios:
            print(f"  inserir {horario:%d/%m %H:%M}")
            arvore.inserir(horario)
        print()
        print(arvore.desenhar())
        print(f"\n{resumo(arvore)}")


def parte_3_cancelamentos(horarios):
    titulo("PARTE 3 - Cancelamentos (remoção com rebalanceamento)")
    cancelar = horarios[:3]
    for Arvore in ESTRUTURAS:
        arvore = Arvore()
        for horario in horarios:
            arvore.inserir(horario)
        arvore.zerar_contadores()
        arvore.verbose = True
        subtitulo(f"{Arvore.nome}: cancelando as 3 primeiras consultas do dia")
        for horario in cancelar:
            print(f"  cancelar {horario:%d/%m %H:%M}")
            arvore.remover(horario)
        print()
        print(arvore.desenhar())
        print(f"\n{resumo(arvore)}")


def parte_4_base_real():
    titulo("PARTE 4 - Base real da clínica (dados/consultas_clinica.csv)")
    print("As consultas do arquivo estão em ordem cronológica, como no dia a dia.\n")
    for Arvore in ESTRUTURAS:
        agenda = Agenda.da_base(Arvore)
        print(f"{Arvore.nome}: {agenda.total_consultas()} consultas agendadas")
        for medico in agenda.medicos():
            arvore = agenda.arvore(medico)
            media = arvore.comparacoes_medias_busca(arvore.chaves())
            print(
                f"   {medico:<18} {len(arvore):>4} consultas | altura {arvore.altura():>3} | "
                f"{media:7.1f} comparações por busca | {arvore.rotacoes:>3} rotações"
            )
        print()


def parte_5_agenda():
    titulo("PARTE 5 - A agenda funcionando (sobre a AVL)")
    agenda = Agenda.da_base()
    medico = "Dra. Marina Souza"
    dia = datetime(2026, 11, 18)

    subtitulo(f"Agenda do dia 18/11 - {medico} (busca por intervalo)")
    for consulta in agenda.agenda_do_dia(medico, dia):
        print(f"  {consulta}")

    subtitulo("Esse horário está livre? (busca)")
    for hora in (8, 9, 10):
        horario = dia.replace(hour=hora)
        livre = "livre" if agenda.horario_livre(medico, horario) else "ocupado"
        print(f"  {horario:%d/%m %H:%M}: {livre}")

    subtitulo("Próximo horário livre a partir das 08:00 (busca horário por horário)")
    livre = agenda.proximo_horario_livre(medico, dia.replace(hour=8))
    print(f"  {livre:%d/%m %H:%M}")

    subtitulo("Agendar nesse horário (inserção) e tentar de novo")
    nova = Consulta(9999, livre, medico, "Paciente Demonstração", "consulta", "agendada")
    print(f"  primeira vez: {'agendada' if agenda.agendar(nova) else 'recusada'}")
    repetida = Consulta(10000, livre, medico, "Outro Paciente", "consulta", "agendada")
    print(f"  mesmo horário de novo: {'agendada' if agenda.agendar(repetida) else 'recusada (ocupado)'}")
    domingo = Consulta(10001, datetime(2026, 11, 22, 9), medico, "Fora do horário", "consulta", "agendada")
    print(f"  num domingo: {'agendada' if agenda.agendar(domingo) else 'recusada (clínica fechada)'}")

    subtitulo("Próxima consulta a partir das 12:00 (sucessor)")
    print(f"  {agenda.proxima_consulta(medico, dia.replace(hour=12))}")

    subtitulo("Remarcar a consulta de demonstração (remoção + inserção)")
    novo_horario = agenda.proximo_horario_livre(medico, dia.replace(day=19, hour=14))
    agenda.remarcar(medico, livre, novo_horario)
    print(f"  {livre:%d/%m %H:%M} -> {novo_horario:%d/%m %H:%M}: {agenda.arvore(medico).buscar(novo_horario)}")

    subtitulo("Cancelar (remoção)")
    cancelada = agenda.cancelar(medico, novo_horario)
    print(f"  cancelada: {cancelada}")
    print(f"  horário livre de novo? {agenda.horario_livre(medico, novo_horario)}")

    subtitulo(f"Semana de 16/11 - {medico}")
    semana = agenda.agenda_da_semana(medico, dia)
    print(f"  {len(semana)} consultas, de {semana[0].data_hora:%d/%m %H:%M} a {semana[-1].data_hora:%d/%m %H:%M}")


def main():
    horarios = gerar_horarios(7)  # manhã de 16/11: 08:00 a 11:00
    parte_1_bst_degenera(horarios)
    parte_2_balanceadas(horarios)
    parte_3_cancelamentos(horarios)
    parte_4_base_real()
    parte_5_agenda()
    print()


if __name__ == "__main__":
    main()
