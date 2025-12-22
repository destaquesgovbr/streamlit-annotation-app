"""
Utilitários para trabalhar com a hierarquia de temas
"""
from typing import Dict, Generator


def iter_all_nodes(tree: Dict) -> Generator[Dict, None, None]:
    """
    Itera sobre todos os nós da árvore

    Yields:
        Dict: Cada nó da árvore
    """
    def _iter_nodes(nodes):
        for node in nodes:
            yield node

            # Recursivamente processar filhos
            if 'children' in node:
                yield from _iter_nodes(node['children'])

    yield from _iter_nodes(tree.get('themes', []))


def get_level(code: str) -> str:
    """
    Determina o nível de um nó baseado no código

    Args:
        code: Código do nó (ex: "01", "01.02", "01.02.03")

    Returns:
        "L1", "L2", ou "L3"
    """
    if not code:
        return "?"

    parts = code.split(".")
    level_map = {1: "L1", 2: "L2", 3: "L3"}
    return level_map.get(len(parts), "?")


def get_theme_hierarchy(tree: Dict) -> Dict[str, Dict]:
    """
    Extrai hierarquia de temas da árvore

    Returns:
        Dict com estrutura: {'L1': {code: label}, 'L2': {parent: {code: label}}, 'L3': {parent: {code: label}}}
    """
    themes = {'L1': {}, 'L2': {}, 'L3': {}}

    for node in iter_all_nodes(tree):
        code = node.get('code', '')
        label = node.get('label', '')
        level = get_level(code)

        if level == 'L1':
            themes['L1'][code] = label
        elif level == 'L2':
            parent_l1 = code.split('.')[0]
            if parent_l1 not in themes['L2']:
                themes['L2'][parent_l1] = {}
            themes['L2'][parent_l1][code] = label
        elif level == 'L3':
            parent_l2 = '.'.join(code.split('.')[:2])
            if parent_l2 not in themes['L3']:
                themes['L3'][parent_l2] = {}
            themes['L3'][parent_l2][code] = label

    return themes
