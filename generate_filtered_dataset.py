#!/usr/bin/env python3
"""
Script para gerar dataset filtrado para anotação.

Filtros aplicados:
- Notícias de 2025
- Com resumo não vazio
- Com classificação temática (L1, L2, L3)

Output: data/test_dataset.csv
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)


def load_from_huggingface(dataset_name: str = "nitaibezerra/govbrnews"):
    """Carrega dataset do HuggingFace"""
    from datasets import load_dataset

    print(f"\n{Fore.CYAN}📥 Carregando dataset: {dataset_name}{Style.RESET_ALL}")
    dataset = load_dataset(dataset_name, split="train")
    print(f"✓ Dataset carregado: {len(dataset):,} documentos")

    return dataset


def apply_filters(df: pd.DataFrame, year: int = 2025, require_summary: bool = True, require_classification: bool = True):
    """
    Aplica filtros ao dataset

    Args:
        df: DataFrame com notícias
        year: Ano para filtrar (padrão: 2025)
        require_summary: Exigir resumo não vazio
        require_classification: Exigir classificação completa (L1, L2, L3)

    Returns:
        DataFrame filtrado
    """
    print(f"\n{Fore.CYAN}🔍 Aplicando filtros{Style.RESET_ALL}")
    print(f"   Dataset original: {len(df):,} notícias")

    # 1. Filtrar por ano
    if 'published_at' in df.columns:
        # Converter para datetime se for string
        df['published_at_dt'] = pd.to_datetime(df['published_at'], errors='coerce')
        df_filtered = df[df['published_at_dt'].dt.year == year].copy()
        print(f"   ✓ Após filtro de ano {year}: {len(df_filtered):,} notícias")
    else:
        print(f"   ⚠️  Coluna 'published_at' não encontrada, pulando filtro de ano")
        df_filtered = df.copy()

    # 2. Filtrar por resumo
    if require_summary and 'summary' in df_filtered.columns:
        # Verificar se resumo existe e não é vazio
        df_filtered = df_filtered[
            df_filtered['summary'].notna() &
            (df_filtered['summary'].str.strip() != '')
        ].copy()
        print(f"   ✓ Após filtro de resumo: {len(df_filtered):,} notícias")
    else:
        if require_summary:
            print(f"   ⚠️  Coluna 'summary' não encontrada, pulando filtro de resumo")

    # 3. Filtrar por classificação
    if require_classification:
        l1_col = 'theme_1_level_1_code'
        l2_col = 'theme_1_level_2_code'
        l3_col = 'theme_1_level_3_code'

        if all(col in df_filtered.columns for col in [l1_col, l2_col, l3_col]):
            df_filtered = df_filtered[
                df_filtered[l1_col].notna() &
                df_filtered[l2_col].notna() &
                df_filtered[l3_col].notna() &
                (df_filtered[l1_col].astype(str).str.strip() != '') &
                (df_filtered[l2_col].astype(str).str.strip() != '') &
                (df_filtered[l3_col].astype(str).str.strip() != '')
            ].copy()
            print(f"   ✓ Após filtro de classificação (L1, L2, L3): {len(df_filtered):,} notícias")
        else:
            print(f"   ⚠️  Colunas de classificação não encontradas, pulando filtro")

    print(f"\n{Fore.GREEN}✓ Filtros aplicados: {len(df):,} → {len(df_filtered):,} notícias{Style.RESET_ALL}")
    reduction_pct = ((len(df) - len(df_filtered)) / len(df)) * 100
    print(f"   Redução: {reduction_pct:.1f}%")

    return df_filtered


def stratified_sample(df: pd.DataFrame, target_size: int = 500, by_field: str = "theme_1_level_1_code"):
    """
    Cria amostra estratificada por tema L1

    Args:
        df: DataFrame filtrado
        target_size: Tamanho desejado da amostra
        by_field: Campo para estratificação

    Returns:
        DataFrame com amostra estratificada
    """
    print(f"\n{Fore.CYAN}📊 Criando amostra estratificada{Style.RESET_ALL}")
    print(f"   Tamanho alvo: {target_size}")

    # Se dataset é menor que tamanho alvo, usar todos
    if len(df) <= target_size:
        print(f"   ⚠️  Dataset ({len(df)}) menor que tamanho alvo ({target_size})")
        print(f"   Usando todas as {len(df)} notícias")
        return df

    # Mostrar distribuição original
    theme_counts = df[by_field].value_counts()
    print(f"\n   Distribuição de temas (top 10):")
    for theme, count in theme_counts.head(10).items():
        pct = (count / len(df)) * 100
        print(f"     {theme}: {count} ({pct:.1f}%)")

    # Estratificar proporcionalmente
    sampled = df.groupby(by_field, group_keys=False).apply(
        lambda x: x.sample(
            n=max(1, int((len(x) / len(df)) * target_size)),
            random_state=42
        )
    ).reset_index(drop=True)

    # Ajustar tamanho
    if len(sampled) > target_size:
        sampled = sampled.sample(n=target_size, random_state=42)
    elif len(sampled) < target_size:
        remaining = target_size - len(sampled)
        extra = df[~df.index.isin(sampled.index)].sample(n=remaining, random_state=42)
        sampled = pd.concat([sampled, extra]).reset_index(drop=True)

    print(f"\n{Fore.GREEN}✓ Amostra criada: {len(sampled)} notícias{Style.RESET_ALL}")

    return sampled


def estimate_complexity(title: str) -> str:
    """Estima complexidade de classificação baseado no título"""
    title_lower = title.lower()

    # Palavras-chave específicas
    specific_keywords = [
        'educação', 'escola', 'universidade', 'ensino',
        'saúde', 'sus', 'hospital', 'vacina',
        'segurança pública', 'polícia', 'prisão',
        'meio ambiente', 'ambiental', 'floresta', 'desmatamento',
        'agricultura', 'safra', 'agropecuária',
        'economia', 'pib', 'inflação', 'dólar',
    ]

    # Palavras genéricas
    generic_keywords = [
        'governo', 'ministro', 'presidente', 'brasil',
        'federal', 'nacional', 'programa', 'projeto',
    ]

    has_specific = any(kw in title_lower for kw in specific_keywords)
    has_generic = any(kw in title_lower for kw in generic_keywords)

    if has_specific and not has_generic:
        return 'clara'
    elif has_generic and not has_specific:
        return 'dificil'
    else:
        return 'moderada'


def prepare_for_annotation(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara DataFrame para anotação"""
    print(f"\n{Fore.CYAN}🔧 Preparando para anotação{Style.RESET_ALL}")

    annotation_df = pd.DataFrame({
        'unique_id': df['unique_id'],
        'titulo': df['title'],
        'resumo': df.get('summary', ''),
        'conteudo_inicio': df['content'].str[:500] if 'content' in df.columns else '',
        'orgao': df.get('agency', ''),
        'data_publicacao': df.get('published_at', ''),
        'url': df.get('url', ''),

        # Campos para anotação (vazios inicialmente)
        'L1_anotado': '',
        'L2_anotado': '',
        'L3_anotado': '',
        'confianca': '',
        'observacoes': '',
        'anotador': '',
        'data_anotacao': '',

        # Ground truth original
        'L1_original': df.get('theme_1_level_1_code', ''),
        'L2_original': df.get('theme_1_level_2_code', ''),
        'L3_original': df.get('theme_1_level_3_code', ''),
    })

    # Adicionar complexidade estimada
    annotation_df['complexidade_estimada'] = annotation_df['titulo'].apply(estimate_complexity)

    print(f"✓ {len(annotation_df)} documentos preparados")

    # Estatísticas
    print(f"\n   Distribuição de complexidade:")
    complexity_dist = annotation_df['complexidade_estimada'].value_counts()
    for level, count in complexity_dist.items():
        pct = (count / len(annotation_df)) * 100
        print(f"     {level}: {count} ({pct:.1f}%)")

    print(f"\n   Verificação de resumos:")
    with_summary = annotation_df['resumo'].notna() & (annotation_df['resumo'].str.strip() != '')
    print(f"     Com resumo: {with_summary.sum()} ({(with_summary.sum()/len(annotation_df)*100):.1f}%)")
    print(f"     Sem resumo: {(~with_summary).sum()} ({((~with_summary).sum()/len(annotation_df)*100):.1f}%)")

    return annotation_df


def save_dataset(df: pd.DataFrame, output_file: Path):
    """Salva dataset preparado"""
    print(f"\n{Fore.CYAN}💾 Salvando dataset{Style.RESET_ALL}")

    # Criar diretório se não existir
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Salvar CSV
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✓ Dataset salvo em: {output_file}")

    # Estatísticas
    print(f"\n{Fore.GREEN}📊 Estatísticas do Dataset Gerado:{Style.RESET_ALL}")
    print(f"   Total de notícias: {len(df)}")
    print(f"   Temas L1 únicos: {df['L1_original'].nunique()}")
    print(f"   Órgãos únicos: {df['orgao'].nunique()}")
    print(f"   Período: {df['data_publicacao'].min()} a {df['data_publicacao'].max()}")


def main():
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Geração de Dataset Filtrado para Anotação{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

    # 1. Carregar dataset
    dataset = load_from_huggingface()
    df = pd.DataFrame(dataset)

    # 2. Aplicar filtros (2025, com resumo, com classificação)
    df_filtered = apply_filters(
        df,
        year=2025,
        require_summary=True,
        require_classification=True
    )

    if len(df_filtered) == 0:
        print(f"\n{Fore.RED}❌ Nenhuma notícia atende aos critérios!{Style.RESET_ALL}")
        return 1

    # 3. Amostra estratificada (se necessário)
    df_sample = stratified_sample(df_filtered, target_size=500)

    # 4. Preparar para anotação
    annotation_df = prepare_for_annotation(df_sample)

    # 5. Salvar
    output_file = Path("data/test_dataset.csv")
    save_dataset(annotation_df, output_file)

    # Sumário final
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Dataset gerado com sucesso!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Próximo passo:{Style.RESET_ALL}")
    print(f"  ./run_local.sh")
    print(f"  (App de anotação rodará em http://localhost:8501)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
