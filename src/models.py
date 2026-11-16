"""Modelo de dados da agenda da clínica.

- Consulta: uma linha da base (dados/consultas_clinica.csv).
- carregar_consultas(): lê o CSV e devolve a lista de consultas.
- gerar_horarios(): gera horários de atendimento sintéticos (usados nos testes
  e no benchmark quando precisamos de mais chaves do que a base tem).
"""

import csv
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

FORMATO_DATA_HORA = "%Y-%m-%d %H:%M"
CAMINHO_BASE = Path(__file__).resolve().parent.parent / "dados" / "consultas_clinica.csv"

# Turnos da clínica: 08:00-11:30 e 14:00-17:30, de 30 em 30 minutos.
HORARIOS_DO_DIA = [time(h, m) for h in (8, 9, 10, 11, 14, 15, 16, 17) for m in (0, 30)]


@dataclass
class Consulta:
    id: int
    data_hora: datetime  # chave da árvore
    medico: str
    paciente: str
    tipo: str  # consulta, retorno ou exame
    status: str  # agendada ou cancelada

    def __str__(self):
        return f"{self.data_hora:%d/%m/%Y %H:%M} | {self.medico} | {self.paciente} ({self.tipo})"


def carregar_consultas(caminho=CAMINHO_BASE):
    """Lê o CSV da clínica e devolve a lista de Consulta, na ordem do arquivo."""
    consultas = []
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            consultas.append(
                Consulta(
                    id=int(linha["id"]),
                    data_hora=datetime.strptime(linha["data_hora"], FORMATO_DATA_HORA),
                    medico=linha["medico"],
                    paciente=linha["paciente"],
                    tipo=linha["tipo"],
                    status=linha["status"],
                )
            )
    return consultas


def gerar_horarios(quantidade, inicio=date(2026, 11, 16)):
    """Gera `quantidade` horários de atendimento em ordem cronológica (só dias úteis)."""
    horarios = []
    dia = inicio
    while len(horarios) < quantidade:
        if dia.weekday() < 5:  # segunda a sexta
            for hora in HORARIOS_DO_DIA:
                horarios.append(datetime.combine(dia, hora))
                if len(horarios) == quantidade:
                    break
        dia += timedelta(days=1)
    return horarios
