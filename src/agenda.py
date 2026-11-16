"""Agenda da clínica: regras de negócio em cima das árvores.

Cada médico tem a sua árvore, com chave = data/hora da consulta. Assim um
mesmo horário nunca é ocupado duas vezes pelo mesmo médico, e a pergunta
"está livre?" é uma busca na árvore daquele médico.

A estrutura usada (BST, AVL ou Rubro-Negra) é escolhida na criação da agenda,
então o mesmo código de negócio roda sobre as três.
"""

from datetime import datetime, timedelta

from .arvores import AVL
from .models import CAMINHO_BASE, HORARIOS_DO_DIA, carregar_consultas

DIAS_DE_BUSCA = 365  # até onde procurar um horário livre


class Agenda:
    def __init__(self, Arvore=AVL):
        self.Arvore = Arvore
        self.arvores = {}  # médico -> árvore com as consultas dele

    @classmethod
    def da_base(cls, Arvore=AVL, caminho=CAMINHO_BASE):
        """Monta a agenda com as consultas agendadas do CSV (as canceladas ficam de fora)."""
        agenda = cls(Arvore)
        for consulta in carregar_consultas(caminho):
            if consulta.status == "agendada":
                agenda.agendar(consulta)
        return agenda

    def arvore(self, medico):
        """Árvore do médico. Só cria uma nova quando é para agendar."""
        if medico not in self.arvores:
            return self.Arvore()  # médico sem consultas: árvore vazia, não cadastrada
        return self.arvores[medico]

    def _arvore_para_escrita(self, medico):
        if medico not in self.arvores:
            self.arvores[medico] = self.Arvore()
        return self.arvores[medico]

    def medicos(self):
        return sorted(self.arvores)

    def total_consultas(self):
        return sum(len(arvore) for arvore in self.arvores.values())

    # ------------------------------------------------------------------
    # Operações do dia a dia
    # ------------------------------------------------------------------
    @staticmethod
    def horario_de_atendimento(data_hora):
        """A clínica só atende em dias úteis, nos horários de 30 em 30 minutos."""
        return data_hora.weekday() < 5 and data_hora.time() in HORARIOS_DO_DIA

    def horario_livre(self, medico, data_hora):
        """Busca: o horário existe na grade e ninguém está marcado nele."""
        return self.horario_de_atendimento(data_hora) and data_hora not in self.arvore(medico)

    def agendar(self, consulta):
        """Inserção. Devolve False se o horário está ocupado ou fora do atendimento."""
        if not self.horario_de_atendimento(consulta.data_hora):
            return False
        return self._arvore_para_escrita(consulta.medico).inserir(consulta.data_hora, consulta)

    def cancelar(self, medico, data_hora):
        """Remoção. Devolve a consulta cancelada, ou None se não havia consulta."""
        arvore = self.arvore(medico)
        consulta = arvore.buscar(data_hora)
        if consulta is None:
            return None
        arvore.remover(data_hora)
        consulta.status = "cancelada"
        return consulta

    def remarcar(self, medico, de, para):
        """Move uma consulta para outro horário (só se o novo estiver livre)."""
        if not self.horario_livre(medico, para):
            return False
        consulta = self.cancelar(medico, de)
        if consulta is None:
            return False
        consulta.data_hora, consulta.status = para, "agendada"
        return self.agendar(consulta)

    def proxima_consulta(self, medico, a_partir_de):
        """Sucessor: primeira consulta marcada a partir de um momento."""
        arvore = self.arvore(medico)
        chave = arvore.a_partir_de(a_partir_de)
        return None if chave is None else arvore.buscar(chave)

    def proximo_horario_livre(self, medico, a_partir_de):
        """Primeiro horário da grade, a partir do momento dado, sem consulta marcada."""
        arvore = self.arvore(medico)
        dia = a_partir_de.date()
        for _ in range(DIAS_DE_BUSCA):
            if dia.weekday() < 5:
                for hora in HORARIOS_DO_DIA:
                    horario = datetime.combine(dia, hora)
                    if horario >= a_partir_de and horario not in arvore:
                        return horario
            dia += timedelta(days=1)
        return None

    def consultas_entre(self, medico, inicio, fim):
        """Busca por intervalo: consultas de inicio até fim (inclusive), em ordem."""
        return [consulta for _, consulta in self.arvore(medico).intervalo(inicio, fim)]

    def agenda_do_dia(self, medico, dia):
        inicio = datetime.combine(dia, datetime.min.time())
        return self.consultas_entre(medico, inicio, inicio + timedelta(days=1, microseconds=-1))

    def agenda_da_semana(self, medico, dia):
        """Consultas de segunda a domingo da semana que contém `dia`."""
        segunda = datetime.combine(dia - timedelta(days=dia.weekday()), datetime.min.time())
        return self.consultas_entre(medico, segunda, segunda + timedelta(days=7, microseconds=-1))
