"""Contrato comum das árvores de busca (BST, AVL e Rubro-Negra).

Tudo o que só LÊ a árvore (buscar, mínimo, sucessor, intervalo, em ordem,
altura, desenho) é igual nas três estruturas e fica aqui. Cada árvore
implementa apenas o que muda: inserir, remover e validar suas regras.

`self._nil` representa o "nó vazio": None na BST e na AVL, e um nó
sentinela preto na Rubro-Negra. Assim os métodos abaixo funcionam nas três.

Os métodos são iterativos de propósito: uma BST com 8.000 datas inseridas em
ordem tem 8.000 níveis, e recursão nessa profundidade estoura o limite do Python.
"""

from collections import deque
from datetime import datetime


def fmt(chave):
    """Formata a chave para exibição (datas ficam curtas: 16/11 08:00)."""
    if isinstance(chave, datetime):
        return chave.strftime("%d/%m %H:%M")
    return str(chave)


class No:
    __slots__ = ("chave", "valor", "esq", "dir", "pai")

    def __init__(self, chave, valor=None, nil=None):
        self.chave = chave
        self.valor = valor
        self.esq = nil
        self.dir = nil
        self.pai = nil


class ArvoreBase:
    nome = "Árvore"

    def __init__(self, verbose=False):
        self._nil = self._criar_nil()
        self.raiz = self._nil  # árvore vazia: a raiz é o próprio "nó vazio"
        self.tamanho = 0
        self.verbose = verbose  # True: imprime cada rotação (usado na demonstração)
        self.comparacoes = 0  # comparações de chave (buscas e inserções)
        self.rotacoes = 0

    def __len__(self):
        return self.tamanho

    def __contains__(self, chave):
        return self._buscar_no(chave) is not self._nil

    def zerar_contadores(self):
        self.comparacoes = 0
        self.rotacoes = 0

    def _log(self, mensagem):
        if self.verbose:
            print(f"    [{self.nome}] {mensagem}")

    def _criar_nil(self):
        """Nó vazio da árvore. A Rubro-Negra redefine para devolver o sentinela preto."""
        return None

    def _novo_no(self, chave, valor):
        """Cria um nó já com os filhos e o pai apontando para o nó vazio."""
        return No(chave, valor, nil=self._nil)

    # ------------------------------------------------------------------
    # A implementar em cada árvore
    # ------------------------------------------------------------------
    def inserir(self, chave, valor=None):
        """Insere a chave. Devolve False se ela já existe (horário ocupado)."""
        raise NotImplementedError

    def remover(self, chave):
        """Remove a chave. Devolve False se ela não existe."""
        raise NotImplementedError

    def validar(self):
        """Confere as regras da árvore. Levanta AssertionError se alguma falhar."""
        self._validar_ordem()

    # ------------------------------------------------------------------
    # Busca
    # ------------------------------------------------------------------
    def _buscar_no(self, chave):
        atual = self.raiz
        while atual is not self._nil:
            self.comparacoes += 1
            if chave == atual.chave:
                return atual
            atual = atual.esq if chave < atual.chave else atual.dir
        return self._nil

    def buscar(self, chave):
        """Devolve o valor guardado na chave, ou None se a chave não existe."""
        no = self._buscar_no(chave)
        return None if no is self._nil else no.valor

    def _minimo_no(self, no):
        while no.esq is not self._nil:
            no = no.esq
        return no

    def minimo(self):
        """Menor chave da árvore (ex.: primeira consulta da agenda)."""
        if self.raiz is self._nil:
            return None
        return self._minimo_no(self.raiz).chave

    def maximo(self):
        if self.raiz is self._nil:
            return None
        no = self.raiz
        while no.dir is not self._nil:
            no = no.dir
        return no.chave

    def a_partir_de(self, chave):
        """Menor chave >= `chave` (sucessor). Ex.: próxima consulta a partir de agora."""
        atual, melhor = self.raiz, None
        while atual is not self._nil:
            self.comparacoes += 1
            if atual.chave == chave:
                return atual.chave
            if atual.chave > chave:
                melhor = atual.chave
                atual = atual.esq
            else:
                atual = atual.dir
        return melhor

    def intervalo(self, inicio, fim):
        """Lista de (chave, valor) com inicio <= chave <= fim, em ordem.

        Só desce nos ramos que podem ter chaves no intervalo.
        """
        resultado, pilha, atual = [], [], self.raiz
        while pilha or atual is not self._nil:
            if atual is not self._nil:
                pilha.append(atual)
                # só vale ir para a esquerda se ainda pode haver chave >= inicio
                atual = atual.esq if atual.chave > inicio else self._nil
                continue
            atual = pilha.pop()
            if atual.chave > fim:
                break
            if atual.chave >= inicio:
                resultado.append((atual.chave, atual.valor))
            atual = atual.dir
        return resultado

    # ------------------------------------------------------------------
    # Percurso e medidas
    # ------------------------------------------------------------------
    def em_ordem(self):
        """Gera (chave, valor) em ordem crescente."""
        pilha, atual = [], self.raiz
        while pilha or atual is not self._nil:
            while atual is not self._nil:
                pilha.append(atual)
                atual = atual.esq
            atual = pilha.pop()
            yield atual.chave, atual.valor
            atual = atual.dir

    def chaves(self):
        return [chave for chave, _ in self.em_ordem()]

    def altura(self):
        """Número de níveis da árvore (vazia = 0, só a raiz = 1)."""
        if self.raiz is self._nil:
            return 0
        niveis, fila = 0, deque([self.raiz])
        while fila:
            niveis += 1
            for _ in range(len(fila)):
                no = fila.popleft()
                if no.esq is not self._nil:
                    fila.append(no.esq)
                if no.dir is not self._nil:
                    fila.append(no.dir)
        return niveis

    def comparacoes_medias_busca(self, chaves):
        """Média de comparações para buscar cada chave da lista."""
        if not chaves:
            return 0.0
        antes = self.comparacoes
        for chave in chaves:
            self._buscar_no(chave)
        total = self.comparacoes - antes
        self.comparacoes = antes  # medir não deve sujar o contador
        return total / len(chaves)

    # ------------------------------------------------------------------
    # Desenho no terminal
    # ------------------------------------------------------------------
    def _rotulo(self, no):
        """Texto de cada nó no desenho. AVL e Rubro-Negra acrescentam informação."""
        return fmt(no.chave)

    def desenhar(self, max_nos=40):
        """Desenha a árvore deitada: raiz à esquerda, filho direito acima, esquerdo abaixo."""
        if self.raiz is self._nil:
            return "(árvore vazia)"
        if self.tamanho > max_nos:
            return f"(árvore com {self.tamanho} nós: grande demais para desenhar)"
        linhas = []
        # pilha de (nó, prefixo, é_filho_direito, é_raiz)
        pilha = [(self.raiz, "", False, True)]
        while pilha:
            no, prefixo, eh_dir, eh_raiz = pilha.pop()
            if isinstance(no, str):  # marcador de linha já pronta
                linhas.append(no)
                continue
            # a linha vertical "│" liga o filho ao pai, que fica do outro lado
            esq_prefixo = prefixo + ("" if eh_raiz else ("│   " if eh_dir else "    "))
            dir_prefixo = prefixo + ("" if eh_raiz else ("    " if eh_dir else "│   "))
            ligacao = "" if eh_raiz else ("┌── " if eh_dir else "└── ")
            # ordem de saída: direita, o próprio nó, esquerda (a pilha inverte)
            if no.esq is not self._nil:
                pilha.append((no.esq, esq_prefixo, False, False))
            pilha.append((prefixo + ligacao + self._rotulo(no), "", False, False))
            if no.dir is not self._nil:
                pilha.append((no.dir, dir_prefixo, True, False))
        return "\n".join(linhas)

    # ------------------------------------------------------------------
    # Validação comum
    # ------------------------------------------------------------------
    def _validar_ordem(self):
        anterior, contagem = None, 0
        for chave, _ in self.em_ordem():
            assert anterior is None or anterior < chave, f"ordem quebrada em {fmt(chave)}"
            anterior = chave
            contagem += 1
        assert contagem == self.tamanho, f"tamanho {self.tamanho}, mas há {contagem} nós"
