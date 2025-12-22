# Testes de Integração

Testes de integração que verificam o funcionamento completo do sistema de anotação.

## Testes Disponíveis

### test_save_annotations.py

Verifica o fluxo completo de salvamento de anotações:

1. **Carregamento de dados**: Testa se o DataLoader carrega o CSV corretamente
2. **Integridade das colunas**: Verifica se todas as colunas necessárias existem
3. **Simulação de anotação**: Cria uma anotação de teste com valores L1, L2, L3
4. **Salvamento**: Persiste os dados no CSV
5. **Recarregamento**: Carrega novamente os dados do disco
6. **Verificação de persistência**: Confirma que os dados foram salvos corretamente

**Problema Crítico Resolvido**: Este teste detectou que os códigos temáticos (L1, L2, L3) estavam perdendo zeros à esquerda ao serem salvos. Por exemplo:
- `'01'` → `'1.0'` ❌
- `'01.01'` → `'1.01'` ❌

**Solução**: Configurar dtype='str' para colunas de códigos temáticos no DataLoader, preservando o formato original:
- `'01'` → `'01'` ✅
- `'01.01'` → `'01.01'` ✅

## Como Executar

```bash
# Executar teste de salvamento
python3 tests/integration/test_save_annotations.py
```

**Pré-requisitos**:
- Dataset de teste deve existir em `data/test_dataset.csv`
- Python 3.11+
- Dependências: `pandas`, `pyyaml`

## Saída Esperada

```
🔍 Testando salvamento de anotações...

1️⃣ Carregando dataset...
   ✅ Dataset carregado: 500 registros

2️⃣ Verificando colunas de anotação...
   ✅ Todas as colunas existem

3️⃣ Simulando anotação no primeiro registro...
   📝 Anotando registro 0:
      L1_anotado: 01
      L2_anotado: 01.01
      L3_anotado: 01.01.01
      confianca: alta
      observacoes: Teste de salvamento automático
      anotador: Test User
      data_anotacao: 2025-12-18T21:33:23.107332

4️⃣ Salvando dataset...
   ✅ Dataset salvo

5️⃣ Recarregando dataset para verificar persistência...
   ✅ Dataset recarregado: 500 registros

6️⃣ Verificando se anotação foi persistida...
   ✅ L1_anotado: '01'
   ✅ L2_anotado: '01.01'
   ✅ L3_anotado: '01.01.01'
   ✅ confianca: 'alta'
   ✅ observacoes: 'Teste de salvamento automático'
   ✅ anotador: 'Test User'
   ✅ data_anotacao: '2025-12-18T21:33:23.107332'

🎉 TESTE PASSOU! Salvamento está funcionando corretamente.

📊 Estatísticas do dataset:
   Total: 500
   Anotadas: 1
   Pendentes: 499
```

## Integração com CI/CD

Para automatizar estes testes no CI/CD, adicione ao workflow:

```yaml
- name: Run Integration Tests
  run: |
    python3 tests/integration/test_save_annotations.py
```

## Próximos Testes

Testes futuros a serem implementados:

- [ ] Teste de concorrência (múltiplos anotadores simultâneos)
- [ ] Teste de rollback (reverter anotações)
- [ ] Teste de filtros (status, complexidade)
- [ ] Teste de navegação (anterior, próxima)
- [ ] Teste de validação (L1 obrigatório)
- [ ] Teste de GCS storage (quando disponível)
