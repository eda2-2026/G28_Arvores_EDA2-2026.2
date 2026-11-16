from .avl import AVL
from .bst import BST
from .rubro_negra import RubroNegra

# Estruturas usadas pela agenda, pelos testes e pelo benchmark.
ESTRUTURAS = (BST, AVL, RubroNegra)

__all__ = ["AVL", "BST", "RubroNegra", "ESTRUTURAS"]
