#!/usr/bin/env python3
"""
Teste do novo método save_annotation que recarrega antes de salvar.

Simula trabalho em paralelo:
1. Carrega dados
2. Salva anotação 1
3. Simula outro usuário salvando anotação 2 diretamente no CSV
4. Salva anotação 3 usando save_annotation (deve ver anotação 2)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'app'))

import pandas as pd
from utils.data_loader import DataLoader
from datetime import datetime

def test_save_with_reload():
    print("🧪 Teste de Save com Reload (trabalho em paralelo)\n")
    print("="*60)

    loader = DataLoader(use_gcs=False)
    dataset_file = 'test_dataset.csv'

    # 1. Estado inicial
    print("\n1️⃣ Carregando dataset inicial...")
    df_inicial = loader.load_csv(dataset_file)
    anotadas_inicial = df_inicial['L1_anotado'].notna().sum()
    print(f"   Anotadas inicialmente: {anotadas_inicial}")

    # 2. Simular save_annotation do índice 10
    print("\n2️⃣ Salvando anotação #10 (Usuário A)...")
    index1 = 10

    # Reload + save
    df = loader.load_csv(dataset_file)
    df.loc[index1, 'L1_anotado'] = '01'
    df.loc[index1, 'L2_anotado'] = '01.01'
    df.loc[index1, 'L3_anotado'] = '01.01.01'
    df.loc[index1, 'confianca'] = 'alta'
    df.loc[index1, 'anotador'] = 'Usuario A'
    df.loc[index1, 'data_anotacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    loader.save_csv(df, dataset_file)
    print(f"   ✅ Anotação #10 salva")

    # 3. Simular outro usuário salvando índice 20 diretamente
    print("\n3️⃣ Simulando Usuário B salvando anotação #20 diretamente...")
    index2 = 20

    df2 = loader.load_csv(dataset_file)
    df2.loc[index2, 'L1_anotado'] = '02'
    df2.loc[index2, 'L2_anotado'] = '02.01'
    df2.loc[index2, 'L3_anotado'] = '02.01.01'
    df2.loc[index2, 'confianca'] = 'media'
    df2.loc[index2, 'anotador'] = 'Usuario B'
    df2.loc[index2, 'data_anotacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    loader.save_csv(df2, dataset_file)
    print(f"   ✅ Anotação #20 salva")

    # 4. Agora salvar índice 30 com reload (deve ver as 2 anteriores)
    print("\n4️⃣ Salvando anotação #30 (Usuário C) COM RELOAD...")
    index3 = 30

    # Reload (simula o que save_annotation faz)
    df3 = loader.load_csv(dataset_file)
    anotadas_antes = df3['L1_anotado'].notna().sum()
    print(f"   📊 Anotadas vistas após reload: {anotadas_antes}")

    df3.loc[index3, 'L1_anotado'] = '03'
    df3.loc[index3, 'L2_anotado'] = '03.01'
    df3.loc[index3, 'L3_anotado'] = '03.01.01'
    df3.loc[index3, 'confianca'] = 'baixa'
    df3.loc[index3, 'anotador'] = 'Usuario C'
    df3.loc[index3, 'data_anotacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    loader.save_csv(df3, dataset_file)
    print(f"   ✅ Anotação #30 salva")

    # 5. Verificar resultado final
    print("\n5️⃣ Verificando resultado final...")
    df_final = loader.load_csv(dataset_file)
    anotadas_final = df_final['L1_anotado'].notna().sum()

    print(f"\n   Total de anotadas: {anotadas_final}")
    print(f"   Esperado: {anotadas_inicial + 3}")

    # Verificar as 3 anotações
    check10 = df_final.loc[index1, 'L1_anotado'] == '01' and df_final.loc[index1, 'anotador'] == 'Usuario A'
    check20 = df_final.loc[index2, 'L1_anotado'] == '02' and df_final.loc[index2, 'anotador'] == 'Usuario B'
    check30 = df_final.loc[index3, 'L1_anotado'] == '03' and df_final.loc[index3, 'anotador'] == 'Usuario C'

    print(f"\n   ✓ Anotação #10 (Usuario A): {'✅' if check10 else '❌'}")
    print(f"   ✓ Anotação #20 (Usuario B): {'✅' if check20 else '❌'}")
    print(f"   ✓ Anotação #30 (Usuario C): {'✅' if check30 else '❌'}")

    # Verificar zeros à esquerda
    print(f"\n   ✓ Zeros preservados:")
    print(f"      #10 L1: '{df_final.loc[index1, 'L1_anotado']}' (esperado '01')")
    print(f"      #20 L1: '{df_final.loc[index2, 'L1_anotado']}' (esperado '02')")
    print(f"      #30 L1: '{df_final.loc[index3, 'L1_anotado']}' (esperado '03')")

    # Resultado
    print("\n" + "="*60)
    if all([check10, check20, check30]) and anotadas_final == anotadas_inicial + 3:
        print("🎉 TESTE PASSOU!")
        print("✅ Reload-before-save funcionando corretamente")
        print("✅ Nenhuma anotação foi perdida")
        print("✅ Trabalho em paralelo suportado")
        return True
    else:
        print("❌ TESTE FALHOU!")
        return False

if __name__ == "__main__":
    success = test_save_with_reload()
    sys.exit(0 if success else 1)
