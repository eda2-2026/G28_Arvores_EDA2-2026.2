"""Árvore Binária de Busca (BST) sem balanceamento.

Regra: tudo à esquerda de um nó é menor que ele, tudo à direita é maior.
Não há rotação: a forma da árvore depende só da ordem de inserção. Se as
datas chegam em ordem cronológica (o normal numa agenda), cada nova consulta
vai para a direita da anterior e a árvore vira uma lista: altura n, busca O(n).

Inserção e remoção são iterativas para aguentar essa degeneração sem estourar
o limite de recursão do Python.
"""

from .base import ArvoreBase


class BST(ArvoreBase):
    nome = "BST"

    def inserir(self, chave, valor=None):
        pai, atual = None, self.raiz
        while atual is not None:
            self.comparacoes += 1
            if chave == atual.chave:
                return False  # horário já ocupado
            pai = atual
            atual = atual.esq if chave < atual.chave else atual.dir

        novo = self._novo_no(chave, valor)
        novo.pai = pai
        if pai is None:
            self.raiz = novo
        elif chave < pai.chave:
            pai.esq = novo
        else:
            pai.dir = novo
        self.tamanho += 1
        return True

    def remover(self, chave):
        no = self._buscar_no(chave)
        if no is None:
            return False

        if no.esq is not None and no.dir is not None:
            # Dois filhos: copia o sucessor (menor da subárvore direita) para cá
            # e remove o sucessor, que tem no máximo um filho (o direito).
            sucessor = self._minimo_no(no.dir)
            no.chave, no.valor = sucessor.chave, sucessor.valor
            no = sucessor

        # Agora `no` tem no máximo um filho: liga esse filho ao avô.
        filho = no.esq if no.esq is not None else no.dir
        self._substituir(no, filho)
        self.tamanho -= 1
        return True

    def _substituir(self, no, filho):
        """Coloca `filho` no lugar de `no` (filho pode ser None)."""
        if filho is not None:
            filho.pai = no.pai
        if no.pai is None:
            self.raiz = filho
        elif no is no.pai.esq:
            no.pai.esq = filho
        else:
            no.pai.dir = filho

    def validar(self):
        super().validar()
        # ponteiros de pai consistentes
        pilha = [self.raiz] if self.raiz is not None else []
        while pilha:
            no = pilha.pop()
            for filho in (no.esq, no.dir):
                if filho is not None:
                    assert filho.pai is no, f"pai errado em {filho.chave}"
                    pilha.append(filho)
        assert self.raiz is None or self.raiz.pai is None, "raiz com pai"
