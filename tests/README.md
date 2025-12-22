# Testes Automatizados - App de Anotação

Testes end-to-end usando Playwright para validar a interface de anotação de notícias.

## 🎯 Modo Direto para Testes

Os testes usam um **modo direto** (`?direct=true`) que:
- ✅ Pula a home page automaticamente
- ✅ Define nome de anotador padrão ("Test User")
- ✅ Vai direto para interface de classificação
- ✅ Evita problemas com reruns do Streamlit

**URL de teste:** `http://localhost:8501?direct=true`

## 📋 Pré-requisitos

1. **App Streamlit rodando**: O app deve estar rodando em `http://localhost:8501`
2. **Python 3.11+**
3. **Dependências de teste instaladas**

## 🚀 Instalação

```bash
# 1. Instalar dependências de teste
pip install -r tests/requirements.txt

# 2. Instalar browsers do Playwright
playwright install
```

## ▶️ Executar Testes

### Todos os testes
```bash
pytest tests/test_annotation_flow.py -v
```

### Testes específicos de uma classe
```bash
# Apenas testes da home page
pytest tests/test_annotation_flow.py::TestHomePage -v

# Apenas testes da interface de anotação
pytest tests/test_annotation_flow.py::TestAnnotationInterface -v

# Apenas testes de emojis de complexidade
pytest tests/test_annotation_flow.py::TestComplexityEmojis -v
```

### Teste específico
```bash
# Teste crítico de reatividade L1→L2
pytest tests/test_annotation_flow.py::TestAnnotationInterface::test_l1_selection_shows_l2_field -v
```

### Com modo headful (ver navegador)
```bash
pytest tests/test_annotation_flow.py -v --headed
```

### Com modo slow-mo (mais lento para visualização)
```bash
pytest tests/test_annotation_flow.py -v --headed --slowmo 1000
```

## 📊 Cobertura de Testes

### TestHomePage
- ✅ Home page carrega corretamente
- ✅ Campo de nome do anotador existe
- ✅ Validação ao tentar iniciar sem nome
- ✅ Início bem-sucedido com nome preenchido

### TestAnnotationInterface
- ✅ Nome do anotador aparece na sidebar
- ✅ Métricas de progresso estão visíveis
- ✅ Filtros têm tooltips
- ✅ Complexidade exibe emoji
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

### TestComplexityEmojis
- ✅ Filtro de complexidade mostra emojis (🟢🟡🔴)

## 🐛 Debugging

### Ver screenshots em caso de falha
```bash
pytest tests/test_annotation_flow.py -v --screenshot=on --video=retain-on-failure
```

### Executar com trace (para análise detalhada)
```bash
pytest tests/test_annotation_flow.py -v --tracing=on
```

### Abrir trace viewer
```bash
playwright show-trace trace.zip
```

## ⚠️ Notas Importantes

1. **App deve estar rodando**: Certifique-se de que o app está acessível em `http://localhost:8501` antes de executar os testes
2. **Timeouts**: Alguns testes usam `wait_for_timeout()` para aguardar animações do Streamlit
3. **Seletores**: Os testes usam `data-testid` do Streamlit e seletores de texto
4. **Rerun**: O Streamlit faz reruns automáticos, então alguns testes aguardam estabilização

## 📝 Adicionar Novos Testes

1. Adicione métodos de teste nas classes existentes ou crie novas classes
2. Use fixture `annotation_page` para testes que requerem acesso à interface de anotação
3. Use `expect()` do Playwright para assertions
4. Adicione `page.wait_for_timeout()` quando necessário para aguardar animações

Exemplo:
```python
def test_nova_funcionalidade(self, annotation_page: Page):
    """Descrição do teste"""
    page = annotation_page

    # Aguardar carregamento
    page.wait_for_timeout(2000)

    # Interagir com elementos
    button = page.locator("text=Meu Botão")
    button.click()

    # Verificar resultado
    expect(page.locator("text=Resultado Esperado")).to_be_visible()
```

## 🔗 Referências

- [Playwright Python Docs](https://playwright.dev/python/docs/intro)
- [Pytest Playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [Streamlit Testing Best Practices](https://docs.streamlit.io/library/advanced-features/testing)
