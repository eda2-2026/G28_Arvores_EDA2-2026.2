# G28_Arvores_EDA2-2026.2

Comparação entre **BST**, **AVL** e **Árvore Rubro-Negra** aplicadas a um sistema de agendamento de consultas de uma clínica.

> **Status: Etapa 1 (em andamento).** Contexto escolhido, modelo de dados definido e base de dados gerada. As implementações das árvores e os experimentos serão adicionados nas próximas etapas (veja [Status do projeto](#status-do-projeto)).

## Cenário

Toda clínica, consultório ou salão precisa de uma agenda: dado um dia e horário, saber se está livre, qual é a próxima consulta e o que há marcado na semana. Neste trabalho cada médico tem uma agenda indexada por **data e horário** (a chave da árvore), de modo que dois pacientes nunca ocupam o mesmo horário com o mesmo médico.

**Por que esse contexto para este trabalho?**

No trabalho anterior (Ordenação) usamos o estoque de uma farmácia. Agora escolhemos um contexto diferente de propósito: consultas são marcadas, em grande parte, **em ordem cronológica**, e chaves que chegam ordenadas são o pior caso de uma BST comum (ela degenera em uma lista encadeada). É exatamente o problema que a AVL e a Rubro-Negra resolvem, então esse contexto deixa a diferença entre as três estruturas evidente.

Operações que a agenda precisa suportar:

| Operação no dia a dia | Operação na árvore |
|---|---|
| Esse horário está livre? | busca |
| Marcar uma consulta | inserção |
| Cancelar uma consulta | remoção (rebalanceamento) |
| Qual o próximo horário disponível? | sucessor |
| O que há marcado nesta semana? | busca por intervalo |

## Objetivos

**MVP**
- Implementar BST, AVL e Rubro-Negra (inserção, busca e remoção).
- Medir altura final, número de rotações, comparações por busca e tempos de execução.
- Aplicar a estrutura numa agenda real (horário livre, próximo horário livre, agenda do dia/semana).

**Extras (planejados)**
- Desenho da árvore no terminal com as rotações aparecendo passo a passo.
- Testes automáticos que validam as regras de cada árvore após cada operação.
- Gráficos comparativos e recomendação para o cliente.

## Tecnologias

- Python 3.10+
- matplotlib (para os gráficos, nas etapas seguintes)

## Base de dados

A base é **simulada**, gerada por script com semente fixa (seed 42), então qualquer integrante gera exatamente o mesmo arquivo.

- Arquivo: [`dados/consultas_clinica.csv`](dados/consultas_clinica.csv)
- Gerador: [`dados/gerar_base.py`](dados/gerar_base.py)

| Característica | Valor |
|---|---|
| Consultas | 2.004 |
| Médicos | 3 (Dra. Marina Souza, Dr. Paulo Lima, Dra. Renata Alves) |
| Período | 16/11/2026 a 05/02/2027 (12 semanas de dias úteis) |
| Horários | de 30 em 30 minutos, 08:00-11:30 e 14:00-17:30 |
| Ocupação simulada | cerca de 70% dos horários |
| Ordem das linhas | cronológica (como as consultas são cadastradas no dia a dia) |

Campos:

| Campo | Descrição |
|---|---|
| `id` | identificador da linha |
| `data_hora` | data e horário da consulta (**chave da árvore**), formato `AAAA-MM-DD HH:MM` |
| `medico` | médico responsável (uma árvore por médico) |
| `paciente` | nome do paciente |
| `tipo` | `consulta`, `retorno` ou `exame` |
| `status` | `agendada` ou `cancelada` |

Regra de integridade: para o mesmo médico, não existem duas consultas com a mesma `data_hora`.

## Estrutura

Estado atual do repositório:

```
├── dados/
│   ├── consultas_clinica.csv   # base de dados simulada
│   └── gerar_base.py           # gerador (seed 42)
└── README.md
```

Estrutura prevista (seguindo o padrão do trabalho anterior):

```
├── assets/                    # gráficos e dados do benchmark
├── dados/
├── src/
│   ├── models.py              # classe Consulta
│   ├── cenarios.py            # cenários de entrada
│   ├── agenda.py              # regras de negócio da agenda
│   └── arvores/
│       ├── base.py            # contrato comum das árvores
│       ├── bst.py
│       ├── avl.py
│       └── rubro_negra.py
├── comparacao.py              # benchmark
├── main.py                    # demonstração
├── plot_results.py            # gráficos
├── testes.py                  # testes de corretude
└── requirements.txt
```

## Como rodar

Por enquanto só é possível gerar a base de dados:

```bash
python dados/gerar_base.py
```

As instruções completas serão atualizadas conforme as próximas etapas forem entregues.

## Status do projeto

- [x] Escolher o contexto (agenda de clínica) e justificar a escolha
- [x] Definir o modelo de dados e as operações da agenda
- [x] Gerar a base de dados simulada
- [ ] Implementar a BST
- [ ] Implementar a AVL
- [ ] Implementar a Rubro-Negra
- [ ] Agenda da clínica e demonstração passo a passo
- [ ] Testes de corretude
- [ ] Benchmark, gráficos e análise experimental
- [ ] Recomendação para o cliente
- [ ] Vídeo de apresentação

## Integrantes

- (nome 1)
- (nome 2)
- (nome 3)

## Vídeo de Apresentação

(link do vídeo)
