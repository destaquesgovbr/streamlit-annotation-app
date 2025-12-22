#!/usr/bin/env python3
"""
Script de teste para verificar se o salvamento de anotações funciona.
"""

import sys
from pathlib import Path
from datetime import datetime

# Adicionar diretório raiz do projeto ao path
# Este script pode ser executado de tests/integration/ ou do diretório raiz
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.data_loader import DataLoader

def test_save_annotation():
    """Testa o fluxo completo de salvamento de anotação"""

    print("🔍 Testando salvamento de anotações...\n")

    # 1. Carregar dados
    print("1️⃣ Carregando dataset...")
    loader = DataLoader(use_gcs=False)
    df = loader.load_csv("test_dataset.csv")
    print(f"   ✅ Dataset carregado: {len(df)} registros\n")

    # 2. Verificar colunas necessárias
    print("2️⃣ Verificando colunas de anotação...")
    required_cols = ['L1_anotado', 'L2_anotado', 'L3_anotado', 'confianca', 'observacoes', 'anotador', 'data_anotacao']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        print(f"   ⚠️ Colunas faltando: {missing_cols}")
        print("   Adicionando colunas...")
        for col in missing_cols:
            df[col] = None
    else:
        print("   ✅ Todas as colunas existem\n")

    # 3. Simular uma anotação no primeiro registro
    print("3️⃣ Simulando anotação no primeiro registro...")
    test_index = df.index[0]

    # Valores de teste
    test_data = {
        'L1_anotado': '01',
        'L2_anotado': '01.01',
        'L3_anotado': '01.01.01',
        'confianca': 'alta',
        'observacoes': 'Teste de salvamento automático',
        'anotador': 'Test User',
        'data_anotacao': datetime.now().isoformat()
    }

    print(f"   📝 Anotando registro {test_index}:")
    for key, value in test_data.items():
        df.at[test_index, key] = value
        print(f"      {key}: {value}")
    print()

    # 4. Salvar
    print("4️⃣ Salvando dataset...")
    loader.save_csv(df, "test_dataset.csv")
    print("   ✅ Dataset salvo\n")

    # 5. Recarregar e verificar
    print("5️⃣ Recarregando dataset para verificar persistência...")
    df_reloaded = loader.load_csv("test_dataset.csv")
    print(f"   ✅ Dataset recarregado: {len(df_reloaded)} registros\n")

    # 6. Verificar se a anotação foi salva
    print("6️⃣ Verificando se anotação foi persistida...")
    success = True
    for key, expected_value in test_data.items():
        actual_value = df_reloaded.at[test_index, key]

        # Converter para string para comparação mais fácil
        actual_str = str(actual_value) if actual_value is not None else None
        expected_str = str(expected_value)

        if actual_str != expected_str:
            print(f"   ❌ {key}: esperado '{expected_str}', obtido '{actual_str}'")
            success = False
        else:
            print(f"   ✅ {key}: '{expected_str}'")

    print()

    # 7. Resultado final
    if success:
        print("🎉 TESTE PASSOU! Salvamento está funcionando corretamente.\n")

        # Estatísticas de anotações
        total = len(df_reloaded)
        anotadas = df_reloaded['L1_anotado'].notna().sum()
        print(f"📊 Estatísticas do dataset:")
        print(f"   Total: {total}")
        print(f"   Anotadas: {anotadas}")
        print(f"   Pendentes: {total - anotadas}")

        return 0
    else:
        print("❌ TESTE FALHOU! Há problemas no salvamento.\n")
        return 1

if __name__ == "__main__":
    exit_code = test_save_annotation()
    sys.exit(exit_code)
