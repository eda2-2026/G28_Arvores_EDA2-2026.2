"""Gera a base de dados simulada da agenda da clínica (dados/consultas_clinica.csv).

Uso:  python dados/gerar_base.py

A base é determinística (seed 42): rodar de novo gera exatamente o mesmo arquivo.
Regras da simulação:
  - 3 médicos, 12 semanas de dias úteis a partir de 16/11/2026;
  - horários de 30 em 30 minutos: 08:00-11:30 e 14:00-17:30 (16 por dia);
  - cada horário de cada médico é ocupado com probabilidade de 70%;
  - no mesmo médico nunca há dois pacientes no mesmo horário (chave única).
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 42
MEDICOS = ["Dra. Marina Souza", "Dr. Paulo Lima", "Dra. Renata Alves"]
INICIO = datetime(2026, 11, 16)           # segunda-feira
SEMANAS = 12
HORAS_MANHA = [(8, 0), (8, 30), (9, 0), (9, 30), (10, 0), (10, 30), (11, 0), (11, 30)]
HORAS_TARDE = [(14, 0), (14, 30), (15, 0), (15, 30), (16, 0), (16, 30), (17, 0), (17, 30)]
OCUPACAO = 0.70

NOMES = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Fábio", "Gabriela", "Heitor", "Iara",
         "João", "Karen", "Lucas", "Mariana", "Nicolas", "Olívia", "Pedro", "Quésia",
         "Rafael", "Sofia", "Thiago", "Úrsula", "Vitor", "Wanda", "Xavier", "Yara", "Zeca"]
SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Pereira", "Costa", "Rodrigues",
              "Almeida", "Nascimento", "Lima", "Araújo", "Ribeiro", "Carvalho", "Gomes",
              "Martins", "Barbosa", "Rocha", "Dias", "Moreira", "Cardoso"]


def gerar():
    rnd = random.Random(SEED)
    linhas = []
    for dia in range(SEMANAS * 7):
        data = INICIO + timedelta(days=dia)
        if data.weekday() >= 5:                       # sem sábado e domingo
            continue
        for hora, minuto in HORAS_MANHA + HORAS_TARDE:
            for medico in MEDICOS:
                if rnd.random() >= OCUPACAO:
                    continue
                paciente = f"{rnd.choice(NOMES)} {rnd.choice(SOBRENOMES)}"
                tipo = rnd.choices(["consulta", "retorno", "exame"], weights=[70, 20, 10])[0]
                status = rnd.choices(["agendada", "cancelada"], weights=[88, 12])[0]
                dh = data.replace(hour=hora, minute=minuto)
                linhas.append((dh.strftime("%Y-%m-%d %H:%M"), medico, paciente, tipo, status))
    # ordem cronológica, como as consultas são cadastradas no dia a dia
    linhas.sort(key=lambda l: (l[0], l[1]))
    return linhas


def main():
    linhas = gerar()
    chaves = [(l[0], l[1]) for l in linhas]
    assert len(chaves) == len(set(chaves)), "horário duplicado para o mesmo médico"
    destino = Path(__file__).resolve().parent / "consultas_clinica.csv"
    with open(destino, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "data_hora", "medico", "paciente", "tipo", "status"])
        for i, l in enumerate(linhas, start=1):
            w.writerow([i, *l])
    print(f"{len(linhas)} consultas salvas em {destino.name}")


if __name__ == "__main__":
    main()
