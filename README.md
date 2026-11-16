# G28_Arvores_EDA2-2026.2

Comparação entre **BST**, **AVL** e **Árvore Rubro-Negra** aplicadas a um sistema de agendamento de consultas de uma clínica.

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

**Extras**
- Desenho da árvore no terminal com as rotações aparecendo passo a passo.
- Testes automáticos que validam as regras de cada árvore após cada operação.
- Gráficos comparativos e recomendação para o cliente.

## Tecnologias

- Python 3.9+
- matplotlib (só para os gráficos; árvores, testes e demonstração não precisam dele)

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

```
├── assets/                     # gráficos PNG e ultimos_resultados.json do benchmark
├── dados/
│   ├── consultas_clinica.csv   # base de dados simulada
│   └── gerar_base.py           # gerador (seed 42)
├── src/
│   ├── models.py               # Consulta, carregar_consultas(), gerar_horarios()
│   ├── agenda.py               # regras de negócio da agenda (uma árvore por médico)
│   ├── cenarios.py             # cenários de entrada do benchmark (seed 42)
│   └── arvores/
│       ├── __init__.py         # ESTRUTURAS: as árvores comparadas
│       ├── base.py             # contrato comum: busca, sucessor, intervalo, altura, desenho
│       ├── bst.py              # árvore binária de busca sem balanceamento
│       └── avl.py              # AVL: rebalanceia com rotações
├── main.py                     # demonstração passo a passo
├── comparacao.py               # benchmark -> assets/ultimos_resultados.json
├── plot_results.py             # JSON -> gráficos em assets/
├── testes.py                   # testes de corretude
├── requirements.txt            # matplotlib
└── README.md
```

A Rubro-Negra (`src/arvores/rubro_negra.py`) entra na próxima etapa. Ao ser incluída em `ESTRUTURAS`, ela passa automaticamente pelos testes, pela demonstração e pelo benchmark.

## Como rodar

Requer Python 3.9+ (conferido em 3.9, 3.12 e 3.15).

```bash
pip install -r requirements.txt   # só o matplotlib, para os gráficos
python testes.py                  # deve terminar com "Todos os testes passaram."
python main.py                    # demonstração passo a passo
python comparacao.py              # benchmark (~40 s); aceita tamanhos: python comparacao.py 1000 5000
python plot_results.py            # gera os gráficos em assets/
python dados/gerar_base.py        # gera de novo a base (sai idêntica, seed 42)
```

## BST (Árvore Binária de Busca)

Arquivo: [`src/arvores/bst.py`](src/arvores/bst.py)

Regra: para cada nó, tudo na subárvore esquerda tem chave menor e tudo na direita tem chave maior. Na agenda, a chave é a data/hora da consulta.

| Operação | Como funciona | Custo |
|---|---|---|
| Buscar | compara com o nó e desce para a esquerda ou direita | O(h) |
| Inserir | desce como na busca e pendura o novo nó numa folha; se o horário já existe, recusa (horário ocupado) | O(h) |
| Remover | folha: só retira. Um filho: o filho sobe. Dois filhos: copia o sucessor (menor da direita) e remove o sucessor | O(h) |
| Próxima consulta a partir de X | guarda o último nó maior que X no caminho da busca | O(h) |
| Agenda do dia/semana | percurso em ordem que só desce nos ramos dentro do intervalo | O(h + k) |

`h` é a altura da árvore e `k` o número de consultas devolvidas.

**O problema:** a BST não se reorganiza. A forma depende só da ordem em que as chaves chegam. Numa agenda as consultas são cadastradas, em grande parte, em ordem cronológica: cada nova data é maior que todas as anteriores e vai sempre para a direita. A árvore vira uma lista encadeada, com `h = n`. Os testes mostram isso: com 8.000 horários em ordem a altura é 8.000, e buscar a última consulta custa 8.000 comparações. Com os mesmos horários embaralhados a altura fica abaixo de 60.

Por isso todas as operações da BST são **iterativas**: uma versão recursiva estouraria o limite de recursão do Python nessa árvore degenerada.

O que é comum às três árvores (busca, sucessor, intervalo, altura, desenho no terminal e contadores de comparações e rotações) fica em [`src/arvores/base.py`](src/arvores/base.py). Cada árvore implementa só `inserir`, `remover` e `validar`.

### Testes

[`testes.py`](testes.py) chama `validar()` (na maioria dos testes, depois de cada operação) e, no fim de cada teste, compara a árvore com um dicionário. O `validar()` confere a ordem das chaves, o tamanho e, na BST, os ponteiros de pai. Cobre árvore vazia, inserção em ordem e aleatória, horário ocupado, os três casos de remoção, 3.000 operações misturadas, sucessor, intervalo, desenho e a carga da base real (uma árvore por médico).

## AVL

Arquivo: [`src/arvores/avl.py`](src/arvores/avl.py)

A AVL é uma BST que se rebalanceia sozinha. Cada nó guarda a própria altura, e o **fator de balanceamento** é `altura(esquerda) - altura(direita)`. A regra é: em todo nó o fator fica entre -1 e +1. Isso garante altura de no máximo cerca de `1,44 · log2(n)`, então busca, inserção e remoção custam O(log n) sempre, mesmo com as datas chegando em ordem.

Inserção e remoção descem como na BST. Na volta da recursão, cada nó do caminho recalcula a altura e, se o fator virou +2 ou -2, aplica a rotação do caso:

| Caso | Fator do nó | Fator do filho | Correção |
|---|---|---|---|
| esquerda-esquerda | +2 | >= 0 | rotação à direita |
| esquerda-direita | +2 | < 0 | rotação à esquerda no filho, depois à direita |
| direita-direita | -2 | <= 0 | rotação à esquerda |
| direita-esquerda | -2 | > 0 | rotação à direita no filho, depois à esquerda |

Rotação à esquerda em `x` (caso direita-direita):

```
  x                 y
   \               / \
    y      ->      x   z
     \
      z
```

Na agenda, as consultas entram em ordem cronológica. Cada nova consulta pende a árvore para a direita, e a AVL corrige com rotações à esquerda. Com `verbose=True` a árvore imprime cada caso e cada rotação. Inserindo 10, 20 e 30, em ordem:

```
    [AVL] caso direita-direita em 10
    [AVL] rotação à esquerda em 10 (20 sobe)
```

O desenho mostra o fator de cada nó:

```
    ┌── 30 [f=+0]
┌── 28 [f=+0]
│   └── 25 [f=+0]
20 [f=-1]
└── 10 [f=+0]
```

Como a altura é O(log n), a AVL pode ser recursiva sem risco de estourar a pilha. Na remoção de um nó com dois filhos, ela copia o sucessor (como a BST) e rebalanceia todo o caminho até a raiz. A diferença está em quantos nós precisam ser corrigidos: na inserção, no máximo um nó se desequilibra (1 rotação simples ou 2 numa dupla) e o resto do caminho volta ao normal. Na remoção, corrigir um nó pode desequilibrar o de cima, então podem ser necessárias rotações em vários nós até a raiz, O(log n) no pior caso.

**Primeiro resultado (testes):** com os mesmos 8.000 horários em ordem que deixam a BST com altura 8.000, a AVL fica com altura 13 e faz em média 12 comparações por busca (11,98), contra 4.000,5 da BST. O preço é rotacionar: foram 7.987 rotações para montar a árvore.

### Testes da AVL

Além de todos os testes comuns (que rodam nas duas árvores), [`testes.py`](testes.py) confere:
- os quatro casos de rotação, com 3 chaves cada (1 rotação nos casos simples, 2 nos duplos);
- a altura com 8.000 datas em ordem dentro do limite teórico;
- o rebalanceamento depois de cancelar metade das consultas;
- a saída do modo `verbose`.

O `validar()` da AVL refaz a altura de cada nó a partir das folhas e confere se a altura guardada está certa e se o fator está entre -1 e +1.

## Agenda da clínica e demonstração

Arquivo: [`src/agenda.py`](src/agenda.py)

A classe `Agenda` guarda uma árvore por médico e traduz cada pedido do dia a dia numa operação da árvore. A estrutura é escolhida na criação (`Agenda(BST)`, `Agenda(AVL)`...), então o mesmo código de negócio roda sobre todas as árvores. `Agenda.da_base()` carrega as consultas agendadas de [`dados/consultas_clinica.csv`](dados/consultas_clinica.csv).

| Método | O que responde | Operação na árvore |
|---|---|---|
| `horario_livre(medico, data_hora)` | esse horário está livre? | busca |
| `agendar(consulta)` | marca a consulta; recusa horário ocupado, fim de semana ou fora da grade | inserção |
| `cancelar(medico, data_hora)` | desmarca e devolve a consulta | busca + remoção |
| `remarcar(medico, de, para)` | muda o horário, se o novo estiver livre | remoção + inserção |
| `proxima_consulta(medico, a_partir_de)` | qual a próxima consulta marcada? | sucessor |
| `proximo_horario_livre(medico, a_partir_de)` | qual o próximo horário vago? | busca horário a horário da grade |
| `agenda_do_dia` / `agenda_da_semana` | o que há marcado no dia/semana | busca por intervalo |

### Demonstração (`python main.py`)

O [`main.py`](main.py) mostra o funcionamento em 5 partes, desenhando as árvores no terminal:

1. **BST com consultas em ordem:** as 7 consultas da manhã entram em ordem e a BST vira uma lista (altura 7).
2. **As mesmas consultas na AVL:** cada rotação aparece no momento em que acontece; no fim a árvore tem altura 3.
3. **Cancelamentos:** remoção com rebalanceamento.
4. **Base real:** as 1.764 consultas agendadas do CSV, uma árvore por médico. Na BST cada médico fica com altura igual ao número de consultas (585, 610 e 569); na AVL, altura 10.
5. **A agenda funcionando:** agenda do dia, horário livre, próximo horário livre, agendar (e a recusa de horário ocupado e de domingo), próxima consulta, remarcar, cancelar e agenda da semana.

Trecho da saída:

```
--- AVL: inserindo em ordem, rotação por rotação ---
  inserir 16/11 08:00
  inserir 16/11 08:30
  inserir 16/11 09:00
    [AVL] caso direita-direita em 16/11 08:00
    [AVL] rotação à esquerda em 16/11 08:00 (16/11 08:30 sobe)
  ...

    ┌── 16/11 11:00 [f=+0]
┌── 16/11 10:30 [f=+0]
│   └── 16/11 10:00 [f=+0]
16/11 09:30 [f=+0]
│   ┌── 16/11 09:00 [f=+0]
└── 16/11 08:30 [f=+0]
    └── 16/11 08:00 [f=+0]

AVL: 7 consultas, altura 3, 4 rotações
```

Os testes da agenda (em [`testes.py`](testes.py)) conferem as regras de negócio em todas as árvores: horário ocupado, outro médico no mesmo horário, fim de semana, horário fora da grade, remarcar, cancelar duas vezes e a agenda do dia e da semana da base real contra o CSV.

## Resultados e análise experimental

Medidos com `python comparacao.py` (tamanhos 1.000, 2.000, 4.000 e 8.000; seed 42; tempos = mediana de 3 execuções; Python 3.15, macOS arm64). Os dados completos estão em [`assets/ultimos_resultados.json`](assets/ultimos_resultados.json).

**Tempos dependem da máquina; altura, rotações e comparações não.** Quem rodar de novo vai ter os mesmos valores de altura, rotações e comparações, e tempos parecidos em proporção.

Cenários ([`src/cenarios.py`](src/cenarios.py)):

| Cenário | O que simula |
|---|---|
| `cronologico` | consultas cadastradas em ordem de data (o normal numa agenda) |
| `aleatorio` | os mesmos horários em ordem embaralhada |
| `cancelamentos` | cadastro em ordem de data e, depois, metade das consultas cancelada em ordem aleatória |
| `base_real` | as 2.004 linhas de `dados/consultas_clinica.csv` numa árvore só (chave = data/hora + médico), na ordem do arquivo; depois as 240 canceladas são removidas |

### Cadastro em ordem de data (n = 8.000)

| | BST | AVL |
|---|---|---|
| Altura | 8.000 | 13 |
| Comparações por busca | 4.000,5 | 11,98 |
| Rotações | 0 | 7.987 |
| Tempo de inserção | 2.033,0 ms | 89,5 ms |

![Altura final](assets/altura.png)

A BST vira uma lista: a altura é igual ao número de consultas, e cada busca percorre em média metade da agenda. A AVL fica com altura 13, praticamente o mínimo possível (log2 8.000 = 12,97). Ela faz quase uma rotação por consulta cadastrada (7.987 para 8.000), porque cada data nova pende a árvore para a direita. Mesmo pagando essas rotações, cadastra 23 vezes mais rápido que a BST.

![Comparações por busca](assets/comparacoes_busca.png)

### Cadastro em ordem aleatória (n = 8.000)

| | BST | AVL |
|---|---|---|
| Altura | 36 | 16 |
| Comparações por busca | 16,55 | 12,23 |
| Rotações | 0 | 5.436 |
| Tempo de inserção | 12,4 ms | 72,2 ms |

![Tempo de inserção](assets/tempo_insercao.png)

Com dados embaralhados a BST fica razoavelmente baixa sem fazer nada e é a mais rápida para cadastrar, porque não tem o custo de recalcular alturas e rotacionar. A AVL continua mais baixa e faz menos comparações por busca (12,2 contra 16,5). Ou seja: **a BST só é boa quando a ordem de chegada das chaves é aleatória, e numa agenda ela não é.**

![Rotações](assets/rotacoes.png)

### Cancelamentos (remover 4.000 de 8.000)

| | BST | AVL |
|---|---|---|
| Tempo de remoção | 800,0 ms | 22,4 ms |
| Rotações na remoção | 0 | 652 |
| Altura depois | 4.000 | 13 |

![Remoção](assets/remocao.png)

Cancelar consultas não conserta a BST: ela continua sendo uma lista, agora com 4.000 nós. Na AVL a remoção precisou de 652 rotações (bem menos que uma por remoção) e a altura continuou 13.

### Base real da clínica (2.004 consultas do CSV)

| | BST | AVL |
|---|---|---|
| Altura | 2.004 | 11 |
| Comparações por busca | 1.002,5 | 9,98 |
| Tempo de inserção | 170,3 ms | 15,6 ms |
| Remoção das 240 canceladas | 18,2 ms | 1,1 ms |

![Base real](assets/base_real.png)

A base real confirma o cenário cronológico: como o arquivo está em ordem de data, a BST degenera completamente, e a AVL responde "esse horário está livre?" com cerca de 10 comparações em vez de 1.000.

## Recomendação para o cliente

Para a agenda da clínica, **não usar a BST simples**: as consultas são cadastradas em ordem de data, que é exatamente o pior caso dela. Com alguns meses de agenda, cada consulta ao sistema passaria a percorrer milhares de registros.

Entre as árvores já comparadas, a recomendação é a **AVL**. Uma agenda é consultada muito mais do que alterada (recepção e pacientes perguntam por horários livres o dia todo), e a AVL mantém a menor altura possível, o que deixa a busca, a próxima consulta e a agenda da semana sempre rápidas. O custo das rotações na inserção é pequeno perto do ganho: mesmo pagando uma rotação por consulta, o cadastro em ordem foi 23 vezes mais rápido que na BST.

Esta recomendação será revisada quando a Rubro-Negra entrar no benchmark: ela tende a rotacionar menos na escrita, o que pode pesar a favor dela numa clínica com muitos cancelamentos e remarcações.

## Status do projeto

- [x] Escolher o contexto (agenda de clínica) e justificar a escolha
- [x] Definir o modelo de dados e as operações da agenda
- [x] Gerar a base de dados simulada
- [x] Implementar a BST
- [x] Implementar a AVL
- [ ] Implementar a Rubro-Negra
- [x] Agenda da clínica e demonstração passo a passo
- [ ] Testes de corretude (BST e AVL prontas)
- [x] Benchmark, gráficos e análise experimental (BST e AVL)
- [x] Recomendação para o cliente (BST e AVL; revisar com a Rubro-Negra)
- [ ] Vídeo de apresentação

## Integrantes

- Enzo Lopes ([@lopes061](https://github.com/lopes061))
- Luan Vinícius ([@luannvi](https://github.com/luannvi))

## Vídeo de Apresentação

(link do vídeo)
