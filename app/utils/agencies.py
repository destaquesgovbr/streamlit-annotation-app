"""
Utilidades para carregamento de agências governamentais.
"""

import yaml
from pathlib import Path
from typing import Dict, Optional


class AgencyLoader:
    """Carrega e fornece acesso aos dados de agências governamentais"""

    def __init__(self, agencies_file: Path):
        """
        Inicializa loader de agências.

        Args:
            agencies_file: Caminho para o arquivo agencies.yaml
        """
        self.agencies_file = agencies_file
        self._agencies = None

    @property
    def agencies(self) -> Dict:
        """Carrega agências sob demanda (lazy loading)"""
        if self._agencies is None:
            with open(self.agencies_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self._agencies = data.get('sources', {})
        return self._agencies

    def get_agency_name(self, sigla: str) -> str:
        """
        Obtém o nome completo de uma agência a partir da sigla.

        Args:
            sigla: Sigla da agência (ex: 'mec', 'saude')

        Returns:
            Nome completo da agência ou a sigla se não encontrada
        """
        if not sigla or sigla not in self.agencies:
            return sigla

        return self.agencies[sigla].get('name', sigla)

    def get_agency_info(self, sigla: str) -> Optional[Dict]:
        """
        Obtém todas as informações de uma agência.

        Args:
            sigla: Sigla da agência

        Returns:
            Dicionário com name, type, parent, url ou None se não encontrada
        """
        return self.agencies.get(sigla)
