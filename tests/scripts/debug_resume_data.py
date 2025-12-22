#!/usr/bin/env python3
"""
Script para debugar dados de resumo no dataset
"""
import pandas as pd

# Carregar CSV
df = pd.read_csv('data/test_dataset.csv')

print("="*60)
print("ANÁLISE DE DADOS DE RESUMO")
print("="*60)
print()

# Estatísticas básicas
total = len(df)
notna = df['resumo'].notna().sum()
isna = df['resumo'].isna().sum()

print(f"Total de notícias: {total}")
print(f"resumo com pd.notna() = True: {notna} ({notna/total*100:.1f}%)")
print(f"resumo com pd.isna() = True: {isna} ({isna/total*100:.1f}%)")
print()

# Verificar strings vazias
df_notna = df[df['resumo'].notna()]
vazias = 0
so_espacos = 0
validas = 0

for idx, row in df_notna.iterrows():
    resumo = row['resumo']
    # Testar a condição exata do código
    if pd.notna(resumo) and resumo:
        # Verifica se é só espaços
        if isinstance(resumo, str) and resumo.strip() == "":
            so_espacos += 1
        else:
            validas += 1
    else:
        # pd.notna retornou True mas a segunda condição falhou
        vazias += 1

print("ENTRE AS NOTÍCIAS COM pd.notna(resumo) = True:")
print(f"  Condição completa PASSA (válidas): {validas}")
print(f"  Condição falha (vazias): {vazias}")
print(f"  Só espaços em branco: {so_espacos}")
print()

# Mostrar exemplos de cada tipo
print("="*60)
print("EXEMPLOS:")
print("="*60)
print()

# Exemplo de notícia COM resumo válido
if validas > 0:
    exemplo_valido = df[df['resumo'].notna()].iloc[0]
    print("1. NOTÍCIA COM RESUMO VÁLIDO:")
    print(f"   Index: {df[df['resumo'].notna()].index[0]}")
    print(f"   Título: {exemplo_valido['titulo'][:60]}...")
    print(f"   Resumo: {str(exemplo_valido['resumo'])[:100]}...")
    print(f"   Tipo: {type(exemplo_valido['resumo'])}")
    print(f"   pd.notna(): {pd.notna(exemplo_valido['resumo'])}")
    print(f"   bool(resumo): {bool(exemplo_valido['resumo'])}")
    print()

# Exemplo de notícia SEM resumo (NaN)
exemplo_sem = df[df['resumo'].isna()].iloc[0]
print("2. NOTÍCIA SEM RESUMO (NaN):")
print(f"   Index: {df[df['resumo'].isna()].index[0]}")
print(f"   Título: {exemplo_sem['titulo'][:60]}...")
print(f"   Resumo: {exemplo_sem['resumo']}")
print(f"   Tipo: {type(exemplo_sem['resumo'])}")
print(f"   pd.notna(): {pd.notna(exemplo_sem['resumo'])}")
print()

# Se houver vazias, mostrar exemplo
if vazias > 0:
    print("3. NOTÍCIA COM RESUMO VAZIO (string vazia):")
    for idx, row in df_notna.iterrows():
        resumo = row['resumo']
        if pd.notna(resumo) and not resumo:
            print(f"   Index: {idx}")
            print(f"   Título: {row['titulo'][:60]}...")
            print(f"   Resumo: '{resumo}'")
            print(f"   Tipo: {type(resumo)}")
            print(f"   Len: {len(resumo)}")
            break
    print()

print("="*60)
print("CONCLUSÃO:")
print("="*60)
print(f"✅ Notícias que DEVEM mostrar resumo: {validas} ({validas/total*100:.1f}%)")
print(f"❌ Notícias que NÃO devem mostrar resumo: {total - validas} ({(total-validas)/total*100:.1f}%)")
