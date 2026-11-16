"""Árvore AVL (Adelson-Velsky e Landis).

É uma BST que se rebalanceia sozinha. Cada nó guarda a própria altura, e o
fator de balanceamento é: altura(esquerda) - altura(direita).
Regra da AVL: em todo nó o fator fica entre -1 e +1.

Depois de cada inserção ou remoção, a volta da recursão recalcula as alturas
e, se algum nó passou a ter fator +2 ou -2, aplica a rotação do caso:

    caso              fator do nó   fator do filho   correção
    esquerda-esquerda     +2         >= 0 (esq)      rotação à direita
    esquerda-direita      +2          < 0 (esq)      esquerda no filho, depois direita
    direita-direita       -2         <= 0 (dir)      rotação à esquerda
    direita-esquerda      -2          > 0 (dir)      direita no filho, depois esquerda

Como a altura fica O(log n), a recursão é rasa (cerca de 1,44 * log2 n níveis)
e pode ser usada sem risco de estourar a pilha.
"""

from .base import ArvoreBase, No, fmt


class NoAVL(No):
    __slots__ = ("altura",)

    def __init__(self, chave, valor=None):
        super().__init__(chave, valor)
        self.altura = 1  # folha tem altura 1 (árvore vazia = 0)


def _altura(no):
    return no.altura if no is not None else 0


def _atualizar(no):
    no.altura = 1 + max(_altura(no.esq), _altura(no.dir))


def _fator(no):
    return _altura(no.esq) - _altura(no.dir)


class AVL(ArvoreBase):
    nome = "AVL"

    # ------------------------------------------------------------------
    # Rotações
    # ------------------------------------------------------------------
    def _rotacao_direita(self, y):
        """
              y              x
             / \\            / \\
            x   C   ->     A   y
           / \\                / \\
          A   B              B   C
        """
        x = y.esq
        y.esq = x.dir
        x.dir = y
        _atualizar(y)
        _atualizar(x)
        self.rotacoes += 1
        self._log(f"rotação à direita em {fmt(y.chave)} ({fmt(x.chave)} sobe)")
        return x

    def _rotacao_esquerda(self, x):
        """
            x                  y
           / \\                / \\
          A   y     ->       x   C
             / \\            / \\
            B   C          A   B
        """
        y = x.dir
        x.dir = y.esq
        y.esq = x
        _atualizar(x)
        _atualizar(y)
        self.rotacoes += 1
        self._log(f"rotação à esquerda em {fmt(x.chave)} ({fmt(y.chave)} sobe)")
        return y

    def _balancear(self, no):
        """Recalcula a altura de `no` e corrige o desequilíbrio, se houver."""
        _atualizar(no)
        fator = _fator(no)

        if fator > 1:  # pesado à esquerda
            if _fator(no.esq) < 0:
                self._log(f"caso esquerda-direita em {fmt(no.chave)}")
                no.esq = self._rotacao_esquerda(no.esq)
            else:
                self._log(f"caso esquerda-esquerda em {fmt(no.chave)}")
            return self._rotacao_direita(no)

        if fator < -1:  # pesado à direita
            if _fator(no.dir) > 0:
                self._log(f"caso direita-esquerda em {fmt(no.chave)}")
                no.dir = self._rotacao_direita(no.dir)
            else:
                self._log(f"caso direita-direita em {fmt(no.chave)}")
            return self._rotacao_esquerda(no)

        return no

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------
    def inserir(self, chave, valor=None):
        tamanho_antes = self.tamanho
        self.raiz = self._inserir(self.raiz, chave, valor)
        return self.tamanho > tamanho_antes

    def _inserir(self, no, chave, valor):
        if no is None:
            self.tamanho += 1
            return NoAVL(chave, valor)
        self.comparacoes += 1
        if chave == no.chave:
            return no  # horário já ocupado: nada muda
        if chave < no.chave:
            no.esq = self._inserir(no.esq, chave, valor)
        else:
            no.dir = self._inserir(no.dir, chave, valor)
        return self._balancear(no)

    # ------------------------------------------------------------------
    # Remoção
    # ------------------------------------------------------------------
    def remover(self, chave):
        tamanho_antes = self.tamanho
        self.raiz = self._remover(self.raiz, chave)
        return self.tamanho < tamanho_antes

    def _remover(self, no, chave):
        if no is None:
            return None  # chave não existe
        if chave < no.chave:
            no.esq = self._remover(no.esq, chave)
        elif chave > no.chave:
            no.dir = self._remover(no.dir, chave)
        else:
            if no.esq is None or no.dir is None:
                # zero ou um filho: o filho (ou None) toma o lugar do nó
                self.tamanho -= 1
                return no.esq if no.esq is not None else no.dir
            # dois filhos: copia o sucessor e remove o sucessor da direita
            sucessor = self._minimo_no(no.dir)
            no.chave, no.valor = sucessor.chave, sucessor.valor
            no.dir = self._remover(no.dir, sucessor.chave)
        return self._balancear(no)

    # ------------------------------------------------------------------
    # Desenho e validação
    # ------------------------------------------------------------------
    def _rotulo(self, no):
        return f"{fmt(no.chave)} [f={_fator(no):+d}]"

    def validar(self):
        super().validar()
        self._validar_no(self.raiz)

    def _validar_no(self, no):
        """Devolve a altura real e confere altura guardada e fator de cada nó."""
        if no is None:
            return 0
        altura_esq = self._validar_no(no.esq)
        altura_dir = self._validar_no(no.dir)
        assert no.altura == 1 + max(altura_esq, altura_dir), f"altura errada em {fmt(no.chave)}"
        assert abs(altura_esq - altura_dir) <= 1, f"fator {altura_esq - altura_dir} em {fmt(no.chave)}"
        return no.altura
