"""Árvore Rubro-Negra: BST balanceada por cores e rotações.

As operações de inserção e remoção seguem os casos clássicos de uma árvore
Rubro-Negra. A sentinela preta representa todas as folhas vazias e permite
tratar raiz, filhos e remoções sem casos especiais baseados em ``None``.
"""

from .base import ArvoreBase, No, fmt

VERMELHO = "vermelho"
PRETO = "preto"


class NoRubroNegro(No):
    __slots__ = ("cor",)

    def __init__(self, chave, valor=None, nil=None):
        super().__init__(chave, valor, nil=nil)
        self.cor = VERMELHO


class RubroNegra(ArvoreBase):
    nome = "Rubro-Negra"

    def __init__(self, verbose=False):
        super().__init__(verbose=verbose)
        self.recoloracoes = 0

    def _criar_nil(self):
        nil = NoRubroNegro(None)
        nil.cor = PRETO
        nil.esq = nil.dir = nil.pai = nil
        return nil

    def _novo_no(self, chave, valor):
        return NoRubroNegro(chave, valor, nil=self._nil)

    def zerar_contadores(self):
        super().zerar_contadores()
        self.recoloracoes = 0

    def _recolorir(self, no, cor):
        """Troca a cor de um nó real e conta apenas mudanças efetivas."""
        if no is not self._nil and no.cor != cor:
            no.cor = cor
            self.recoloracoes += 1

    # ------------------------------------------------------------------
    # Rotações
    # ------------------------------------------------------------------
    def _rotacao_esquerda(self, x):
        y = x.dir
        x.dir = y.esq
        if y.esq is not self._nil:
            y.esq.pai = x
        y.pai = x.pai
        if x.pai is self._nil:
            self.raiz = y
        elif x is x.pai.esq:
            x.pai.esq = y
        else:
            x.pai.dir = y
        y.esq = x
        x.pai = y
        self.rotacoes += 1
        self._log(f"rotação à esquerda em {fmt(x.chave)} ({fmt(y.chave)} sobe)")

    def _rotacao_direita(self, y):
        x = y.esq
        y.esq = x.dir
        if x.dir is not self._nil:
            x.dir.pai = y
        x.pai = y.pai
        if y.pai is self._nil:
            self.raiz = x
        elif y is y.pai.dir:
            y.pai.dir = x
        else:
            y.pai.esq = x
        x.dir = y
        y.pai = x
        self.rotacoes += 1
        self._log(f"rotação à direita em {fmt(y.chave)} ({fmt(x.chave)} sobe)")

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------
    def inserir(self, chave, valor=None):
        pai, atual = self._nil, self.raiz
        while atual is not self._nil:
            self.comparacoes += 1
            if chave == atual.chave:
                return False
            pai = atual
            atual = atual.esq if chave < atual.chave else atual.dir

        novo = self._novo_no(chave, valor)
        novo.pai = pai
        if pai is self._nil:
            self.raiz = novo
        elif chave < pai.chave:
            pai.esq = novo
        else:
            pai.dir = novo
        self.tamanho += 1
        self._corrigir_insercao(novo)
        return True

    def _corrigir_insercao(self, no):
        while no.pai.cor == VERMELHO:
            if no.pai is no.pai.pai.esq:
                tio = no.pai.pai.dir
                if tio.cor == VERMELHO:
                    self._log(f"recoloração no caso de tio vermelho em {fmt(no.pai.pai.chave)}")
                    self._recolorir(no.pai, PRETO)
                    self._recolorir(tio, PRETO)
                    self._recolorir(no.pai.pai, VERMELHO)
                    no = no.pai.pai
                else:
                    if no is no.pai.dir:
                        self._log(f"caso esquerda-direita em {fmt(no.pai.pai.chave)}")
                        no = no.pai
                        self._rotacao_esquerda(no)
                    else:
                        self._log(f"caso esquerda-esquerda em {fmt(no.pai.pai.chave)}")
                    self._recolorir(no.pai, PRETO)
                    self._recolorir(no.pai.pai, VERMELHO)
                    self._rotacao_direita(no.pai.pai)
            else:
                tio = no.pai.pai.esq
                if tio.cor == VERMELHO:
                    self._log(f"recoloração no caso de tio vermelho em {fmt(no.pai.pai.chave)}")
                    self._recolorir(no.pai, PRETO)
                    self._recolorir(tio, PRETO)
                    self._recolorir(no.pai.pai, VERMELHO)
                    no = no.pai.pai
                else:
                    if no is no.pai.esq:
                        self._log(f"caso direita-esquerda em {fmt(no.pai.pai.chave)}")
                        no = no.pai
                        self._rotacao_direita(no)
                    else:
                        self._log(f"caso direita-direita em {fmt(no.pai.pai.chave)}")
                    self._recolorir(no.pai, PRETO)
                    self._recolorir(no.pai.pai, VERMELHO)
                    self._rotacao_esquerda(no.pai.pai)
        self._recolorir(self.raiz, PRETO)

    # ------------------------------------------------------------------
    # Remoção
    # ------------------------------------------------------------------
    def remover(self, chave):
        removido = self._buscar_no(chave)
        if removido is self._nil:
            return False

        movido = removido
        cor_original = movido.cor
        if removido.esq is self._nil:
            substituto = removido.dir
            self._transplantar(removido, removido.dir)
        elif removido.dir is self._nil:
            substituto = removido.esq
            self._transplantar(removido, removido.esq)
        else:
            movido = self._minimo_no(removido.dir)
            cor_original = movido.cor
            substituto = movido.dir
            if movido.pai is removido:
                substituto.pai = movido
            else:
                self._transplantar(movido, movido.dir)
                movido.dir = removido.dir
                movido.dir.pai = movido
            self._transplantar(removido, movido)
            movido.esq = removido.esq
            movido.esq.pai = movido
            self._recolorir(movido, removido.cor)

        self.tamanho -= 1
        if cor_original == PRETO:
            self._corrigir_remocao(substituto)
        if self.raiz is not self._nil:
            self.raiz.pai = self._nil
        # A sentinela usa o pai temporário durante a correção; ao final volta
        # a ser totalmente autocontida para a próxima operação/validação.
        self._nil.pai = self._nil
        return True

    def _transplantar(self, antigo, novo):
        if antigo.pai is self._nil:
            self.raiz = novo
        elif antigo is antigo.pai.esq:
            antigo.pai.esq = novo
        else:
            antigo.pai.dir = novo
        novo.pai = antigo.pai

    def _corrigir_remocao(self, no):
        while no is not self.raiz and no.cor == PRETO:
            if no is no.pai.esq:
                irmao = no.pai.dir
                if irmao.cor == VERMELHO:
                    self._log(f"caso de irmão vermelho à direita de {fmt(no.pai.chave)}")
                    self._recolorir(irmao, PRETO)
                    self._recolorir(no.pai, VERMELHO)
                    self._rotacao_esquerda(no.pai)
                    irmao = no.pai.dir
                if irmao.esq.cor == PRETO and irmao.dir.cor == PRETO:
                    self._log(f"caso de dois filhos pretos à direita de {fmt(no.pai.chave)}")
                    self._recolorir(irmao, VERMELHO)
                    no = no.pai
                else:
                    if irmao.dir.cor == PRETO:
                        self._log(f"caso interno de remoção à direita de {fmt(no.pai.chave)}")
                        self._recolorir(irmao.esq, PRETO)
                        self._recolorir(irmao, VERMELHO)
                        self._rotacao_direita(irmao)
                        irmao = no.pai.dir
                    self._log(f"caso externo de remoção à direita de {fmt(no.pai.chave)}")
                    self._recolorir(irmao, no.pai.cor)
                    self._recolorir(no.pai, PRETO)
                    self._recolorir(irmao.dir, PRETO)
                    self._rotacao_esquerda(no.pai)
                    no = self.raiz
            else:
                irmao = no.pai.esq
                if irmao.cor == VERMELHO:
                    self._log(f"caso de irmão vermelho à esquerda de {fmt(no.pai.chave)}")
                    self._recolorir(irmao, PRETO)
                    self._recolorir(no.pai, VERMELHO)
                    self._rotacao_direita(no.pai)
                    irmao = no.pai.esq
                if irmao.dir.cor == PRETO and irmao.esq.cor == PRETO:
                    self._log(f"caso de dois filhos pretos à esquerda de {fmt(no.pai.chave)}")
                    self._recolorir(irmao, VERMELHO)
                    no = no.pai
                else:
                    if irmao.esq.cor == PRETO:
                        self._log(f"caso interno de remoção à esquerda de {fmt(no.pai.chave)}")
                        self._recolorir(irmao.dir, PRETO)
                        self._recolorir(irmao, VERMELHO)
                        self._rotacao_esquerda(irmao)
                        irmao = no.pai.esq
                    self._log(f"caso externo de remoção à esquerda de {fmt(no.pai.chave)}")
                    self._recolorir(irmao, no.pai.cor)
                    self._recolorir(no.pai, PRETO)
                    self._recolorir(irmao.esq, PRETO)
                    self._rotacao_direita(no.pai)
                    no = self.raiz
        self._recolorir(no, PRETO)

    # ------------------------------------------------------------------
    # Desenho e validação
    # ------------------------------------------------------------------
    def _rotulo(self, no):
        sigla = "V" if no.cor == VERMELHO else "P"
        return f"{fmt(no.chave)} [{sigla}]"

    def validar(self):
        super().validar()
        assert self._nil.cor == PRETO, "sentinela não é preta"
        assert self._nil.esq is self._nil and self._nil.dir is self._nil, "filhos da sentinela inconsistentes"
        assert self._nil.pai is self._nil, "pai da sentinela inconsistente"
        if self.raiz is self._nil:
            return
        assert self.raiz.cor == PRETO, "raiz não é preta"
        assert self.raiz.pai is self._nil, "raiz com pai incorreto"
        self._validar_no(self.raiz)

    def _validar_no(self, no):
        """Confere cores, pais e a mesma altura preta em todos os caminhos."""
        if no is self._nil:
            return 1
        assert no.cor in (VERMELHO, PRETO), f"cor inválida em {fmt(no.chave)}"
        for filho in (no.esq, no.dir):
            assert filho is self._nil or filho.pai is no, f"pai incorreto em {fmt(filho.chave)}"
        if no.cor == VERMELHO:
            assert no.esq.cor == PRETO and no.dir.cor == PRETO, f"nó vermelho com filho vermelho em {fmt(no.chave)}"
        pretos_esq = self._validar_no(no.esq)
        pretos_dir = self._validar_no(no.dir)
        assert pretos_esq == pretos_dir, f"alturas pretas diferentes em {fmt(no.chave)}"
        return pretos_esq + (1 if no.cor == PRETO else 0)
