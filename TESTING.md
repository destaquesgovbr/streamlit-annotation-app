# 🧪 Estratégia de Testes - App de Anotação

Este documento descreve a estratégia completa de testes do aplicativo de anotação de notícias governamentais brasileiras.

## 📋 Visão Geral

O app possui **3 camadas de testes**:

1. **Testes de Integração**: Validam funcionalidades core sem UI
2. **Testes E2E (Playwright)**: Validam fluxo completo da interface
3. **Testes Manuais**: Checklist para validação humana

## 🚀 Execução Rápida

```bash
# Todos os testes (integração + E2E)
./run_all_tests.sh

# Com navegador visível
./run_all_tests.sh --headed

# Com slow-motion (1s delay)
./run_all_tests.sh --slow

# Apenas testes de integração
python3 tests/integration/test_save_annotations.py

# Apenas testes E2E
pytest tests/test_annotation_flow.py -v

# Apenas testes manuais
# Seguir checklist em TESTE_MANUAL.md
```

---

## 1️⃣ Testes de Integração

**Localização**: `tests/integration/`

### test_save_annotations.py

**Objetivo**: Validar o fluxo completo de salvamento de anotações no nível de dados.

**O que testa**:
- ✅ Carregamento de CSV via DataLoader
- ✅ Integridade de colunas necessárias
- ✅ Simulação de anotação (L1, L2, L3)
- ✅ Persistência no disco
- ✅ Preservação de zeros à esquerda em códigos (`'01'` não vira `'1.0'`)
- ✅ Consistência após recarregar dados

**Execução**:
```bash
python3 tests/integration/test_save_annotations.py
```

**Saída esperada**:
```
🎉 TESTE PASSOU! Salvamento está funcionando corretamente.

📊 Estatísticas do dataset:
   Total: 500
   Anotadas: 1
   Pendentes: 499
```

**Importância**: Este teste detectou um **bug crítico** onde códigos temáticos perdiam zeros à esquerda ao serem salvos (pandas interpretava como float).

---

## 2️⃣ Testes E2E (End-to-End)

**Localização**: `tests/test_annotation_flow.py`
**Framework**: Playwright + pytest
**Documentação**: `tests/README.md`

### Modo Direto (`?direct=true`)

Para evitar problemas com reruns do Streamlit, os testes usam **modo direto** que:
- Pula a home page
- Define nome padrão "Test User"
- Vai direto para interface de anotação
- **URL**: `http://localhost:8501?direct=true`

### Classes de Teste

#### TestHomePage (4 testes)
Valida página inicial e fluxo de entrada:
- ✅ Home page carrega corretamente
- ✅ Campo de nome do anotador existe
- ✅ Validação ao tentar iniciar sem nome
- ✅ Início bem-sucedido com nome preenchido

#### TestAnnotationInterface (14 testes)
Valida interface principal de anotação:
- ✅ Nome do anotador aparece na sidebar
- ✅ Métricas de progresso visíveis
- ✅ Filtros têm tooltips
- ✅ Complexidade exibe emoji (🟢🟡🔴)
- ✅ Agência mostra nome completo (não sigla)
- ✅ unique_id NÃO é exibido
- ✅ **CRÍTICO**: L1 selecionado → campo L2 aparece
- ✅ **CRÍTICO**: L2 selecionado → campo L3 aparece
- ✅ Ground truth mostra código E label
- ✅ Botões de navegação funcionam
- ✅ Slider de confiança existe
- ✅ Campo de observações existe
- ✅ Validação de L1 obrigatório
- ✅ Botão "Voltar para Home" funciona

#### TestComplexityEmojis (1 teste)
Valida emojis de complexidade:
- ✅ Filtro de complexidade mostra emojis (🟢🟡🔴)

### Execução

```bash
# Todos os testes E2E
pytest tests/test_annotation_flow.py -v

# Testes de uma classe específica
pytest tests/test_annotation_flow.py::TestHomePage -v
pytest tests/test_annotation_flow.py::TestAnnotationInterface -v

# Teste específico
pytest tests/test_annotation_flow.py::TestAnnotationInterface::test_l1_selection_shows_l2_field -v

# Com navegador visível
pytest tests/test_annotation_flow.py -v --headed

# Com slow-motion
pytest tests/test_annotation_flow.py -v --headed --slowmo 1000
```

### Status Atual

**19/19 testes passando** ✅

---

## 3️⃣ Testes Manuais

**Localização**: `TESTE_MANUAL.md`

### Objetivo
Validação humana de aspectos de UX que são difíceis de automatizar:
- Qualidade visual
- Fluidez de animações
- Clareza de instruções
- Conforto cognitivo durante anotação

### Checklist (18 testes)

1. Home Page
2. Validação do Nome
3. Iniciar Anotação
4. Sidebar - Nome do Anotador
5. Sidebar - Métricas de Progresso
6. Sidebar - Filtros com Tooltips
7. Conteúdo da Notícia - Agência
8. Conteúdo da Notícia - Complexidade com Emoji
9. Conteúdo da Notícia - Unique ID NÃO Visível
10. **Classificação Hierárquica L1→L2→L3** (CRÍTICO)
11. Formulário de Avaliação
12. Botões de Ação
13. Validação de Salvamento
14. Salvamento Bem-sucedido
15. Ground Truth - Código E Label
16. Navegação entre Notícias
17. Voltar para Home
18. Filtros Funcionando

---

## 🐛 Bugs Críticos Resolvidos

### 1. Perda de Zeros à Esquerda
**Problema**: Códigos `'01'` viravam `'1.0'` ao salvar
**Causa**: Pandas interpretava como float
**Solução**: Configurar `dtype='str'` no DataLoader
**Commit**: `42f4e99`

### 2. Reatividade L1→L2→L3 Não Funcionava
**Problema**: Selecionar L1 não mostrava campo L2
**Causa**: Seleção dentro de `st.form()` não reage
**Solução**: Mover seleção para FORA do form
**Commit**: `8b0de24`

### 3. Botão Salvar Não Re-desabilitava
**Problema**: Deselecionar L1 não desabilitava botão
**Causa**: Comparação `l1_selected == ""` não funcionava com strings vazias
**Solução**: Usar `str(l1_selected).strip() == ""`
**Commit**: `307b70b`

### 4. Testes Playwright Falhavam por Reruns
**Problema**: Navegação home→anotação falhava aleatoriamente
**Causa**: Streamlit faz reruns automáticos
**Solução**: Criar modo direto (`?direct=true`)
**Commit**: `d7c321d`

---

## 📊 Cobertura de Testes

| Funcionalidade | Integração | E2E | Manual |
|----------------|------------|-----|--------|
| Salvamento de dados | ✅ | ❌ | ✅ |
| Preservação de códigos | ✅ | ❌ | ✅ |
| Home page | ❌ | ✅ | ✅ |
| Validação de nome | ❌ | ✅ | ✅ |
| Interface de anotação | ❌ | ✅ | ✅ |
| Reatividade L1→L2→L3 | ❌ | ✅ | ✅ |
| Formulário | ❌ | ✅ | ✅ |
| Ground truth | ❌ | ✅ | ✅ |
| Navegação | ❌ | ✅ | ✅ |
| Filtros | ❌ | ✅ | ✅ |
| Métricas de progresso | ❌ | ✅ | ✅ |
| Complexidade com emojis | ❌ | ✅ | ✅ |
| Agência (nome completo) | ❌ | ✅ | ✅ |

**Total de testes automatizados**: 20 (1 integração + 19 E2E)
**Total de testes manuais**: 18

---

## 🔄 Integração Contínua (CI/CD)

### GitHub Actions Sugerido

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r tests/requirements.txt
          playwright install

      - name: Start Streamlit app
        run: |
          ./run_local.sh &
          sleep 10  # Wait for app to start

      - name: Run integration tests
        run: |
          python3 tests/integration/test_save_annotations.py

      - name: Run E2E tests
        run: |
          pytest tests/test_annotation_flow.py -v

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-results
          path: test-results/
```

---

## 📝 Próximos Testes a Implementar

### Integração
- [ ] Teste de concorrência (múltiplos anotadores simultâneos)
- [ ] Teste de rollback (reverter anotações)
- [ ] Teste de GCS storage (quando disponível)
- [ ] Teste de carregamento de themes YAML

### E2E
- [ ] Teste de anotação completa (preencher todos os campos e salvar)
- [ ] Teste de navegação completa (anterior/próxima)
- [ ] Teste de filtros combinados (status + complexidade)
- [ ] Teste de performance (tempo de carregamento)

### Performance
- [ ] Benchmark de carregamento de dataset grande (5000+ notícias)
- [ ] Benchmark de salvamento
- [ ] Teste de memória com datasets grandes

---

## 🛠️ Ferramentas Utilizadas

- **pytest**: Framework de testes
- **Playwright**: Automação de browser para E2E
- **pandas**: Manipulação de dados
- **pyyaml**: Parsing de configurações

---

## 📞 Suporte

Em caso de falhas nos testes:

1. **Verificar pré-requisitos**:
   ```bash
   # App rodando?
   curl http://localhost:8501

   # Dependências instaladas?
   pip list | grep -E "(pytest|playwright|pandas|pyyaml)"

   # Browsers do Playwright instalados?
   playwright install
   ```

2. **Executar com debug**:
   ```bash
   pytest tests/test_annotation_flow.py -v --headed --slowmo 1000
   ```

3. **Verificar logs do Streamlit**:
   ```bash
   # Logs do app
   tail -f ~/.streamlit/logs/streamlit.log
   ```

4. **Criar issue no GitHub**:
   - Incluir saída do teste falhado
   - Incluir screenshot (se E2E)
   - Incluir versão do Python e dependências

---

## ✅ Status Final

| Categoria | Status | Cobertura |
|-----------|--------|-----------|
| Testes de Integração | ✅ 100% | 1/1 passando |
| Testes E2E | ✅ 100% | 19/19 passando |
| Testes Manuais | ✅ Documentado | 18 checkpoints |
| Bugs Críticos | ✅ Resolvidos | 4/4 corrigidos |

**🎉 App pronto para uso em produção!**
