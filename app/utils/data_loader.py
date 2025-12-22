"""
Utilitários para carregar/salvar dados (local ou GCS)
"""
import os
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
import yaml


class DataLoader:
    """Carregador de dados com suporte a local e GCS"""

    def __init__(self, use_gcs: bool = False, bucket_name: Optional[str] = None):
        """
        Args:
            use_gcs: Se True, usa Google Cloud Storage
            bucket_name: Nome do bucket GCS (se use_gcs=True)
        """
        self.use_gcs = use_gcs
        self.bucket_name = bucket_name

        if use_gcs and not bucket_name:
            # Tentar obter do environment
            self.bucket_name = os.getenv('GCS_BUCKET', 'dgb-streamlit-data')

        # Paths locais (fallback)
        self.local_data_dir = Path(__file__).parent.parent.parent / "data"
        self.local_data_dir.mkdir(exist_ok=True)

    def load_csv(self, filename: str) -> pd.DataFrame:
        """Carrega CSV (local ou GCS)"""
        if self.use_gcs:
            return self._load_csv_gcs(filename)
        else:
            return self._load_csv_local(filename)

    def save_csv(self, df: pd.DataFrame, filename: str):
        """Salva CSV (local ou GCS)"""
        if self.use_gcs:
            self._save_csv_gcs(df, filename)
        else:
            self._save_csv_local(df, filename)

    def load_yaml(self, filename: str) -> Dict:
        """Carrega YAML (local ou GCS)"""
        if self.use_gcs:
            return self._load_yaml_gcs(filename)
        else:
            return self._load_yaml_local(filename)

    # Métodos locais
    def _load_csv_local(self, filename: str) -> pd.DataFrame:
        """Carrega CSV local com tipos corretos para códigos temáticos"""
        filepath = self.local_data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

        # Definir dtypes para colunas de código temático como string para preservar zeros à esquerda
        dtype_dict = {
            'L1_original': str,
            'L2_original': str,
            'L3_original': str,
            'L1_anotado': str,
            'L2_anotado': str,
            'L3_anotado': str
        }

        return pd.read_csv(filepath, dtype=dtype_dict, keep_default_na=True)

    def _save_csv_local(self, df: pd.DataFrame, filename: str):
        """Salva CSV local"""
        filepath = self.local_data_dir / filename
        df.to_csv(filepath, index=False, encoding='utf-8')

    def _load_yaml_local(self, filename: str) -> Dict:
        """Carrega YAML local"""
        filepath = self.local_data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    # Métodos GCS
    def _load_csv_gcs(self, filename: str) -> pd.DataFrame:
        """Carrega CSV do GCS com tipos corretos para códigos temáticos"""
        from google.cloud import storage
        from io import StringIO

        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(filename)

        # Download para memória
        content = blob.download_as_text()

        # Definir dtypes para colunas de código temático como string para preservar zeros à esquerda
        dtype_dict = {
            'L1_original': str,
            'L2_original': str,
            'L3_original': str,
            'L1_anotado': str,
            'L2_anotado': str,
            'L3_anotado': str
        }

        return pd.read_csv(StringIO(content), dtype=dtype_dict, keep_default_na=True)

    def _save_csv_gcs(self, df: pd.DataFrame, filename: str):
        """Salva CSV no GCS"""
        from google.cloud import storage
        from io import StringIO

        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(filename)

        # Upload da memória
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        blob.upload_from_string(csv_buffer.getvalue(), content_type='text/csv')

    def _load_yaml_gcs(self, filename: str) -> Dict:
        """Carrega YAML do GCS"""
        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(filename)

        content = blob.download_as_text()
        return yaml.safe_load(content)
