# Roteiro de Teste Manual - App de Anotação

## 🎯 Objetivo
Validar todas as correções de UX implementadas no app de anotação de notícias.

## 📋 Checklist de Testes

### 1. Home Page ✅
**URL:** http://localhost:8501

- [ ] Página carrega com título "📋 Anotação Manual de Notícias GovBR"
- [ ] Seção "🎯 Objetivo" está visível e clara
- [ ] Seção "📝 Como Anotar" explica o processo passo a passo
- [ ] Seção "✅ Dicas de Qualidade" fornece orientações
- [ ] Seção "🚀 Filtros Disponíveis" lista os filtros com emojis corretos:
  - 🟢 Clara: Tema óbvio
  - 🟡 Moderada: Requer análise
  - 🔴 Difícil: Ambígua ou multi-temática
- [ ] Campo "Seu Nome" está visível
- [ ] Botão "🚀 Iniciar Anotação" está presente

### 2. Validação do Nome ✅
**Ação:** Clicar em "Iniciar Anotação" SEM preencher o nome

**Resultado esperado:**
- [ ] Mensagem de erro: "⚠️ Por favor, informe seu nome antes de iniciar"

### 3. Iniciar Anotação ✅
**Ação:** Preencher nome (ex: "João Silva") e clicar "Iniciar Anotação"

**Resultado esperado:**
- [ ] App navega para interface de anotação
- [ ] Home page desaparece
- [ ] Interface de anotação carrega

### 4. Sidebar - Nome do Anotador ✅
**Verificar na sidebar (barra lateral esquerda):**

- [ ] Nome do anotador aparece no topo: "👤 João Silva"
- [ ] Botão "🏠 Voltar para Home" está visível

### 5. Sidebar - Métricas de Progresso ✅
**Verificar na sidebar:**

- [ ] Seção "📊 Progresso" está visível
- [ ] Métrica "Total" mostra número de notícias
- [ ] Métrica "Anotadas" mostra quantidade e percentual
- [ ] Métrica "Pendentes" mostra quantidade restante
- [ ] Barra de progresso visual está presente

### 6. Sidebar - Filtros com Tooltips ✅
**Verificar na sidebar:**

- [ ] Seção "🔍 Filtros" está visível
- [ ] Filtro "Status" tem tooltip (passar mouse/clicar no ícone de ajuda)
- [ ] Filtro "Complexidade" tem tooltip
- [ ] Filtro de complexidade mostra emojis nas opções:
  - 🟢 clara
  - 🟡 moderada
  - 🔴 dificil

### 7. Conteúdo da Notícia - Agência ✅
**Verificar no conteúdo principal:**

- [ ] Campo "Órgão" mostra NOME COMPLETO da agência
  - ✅ Exemplo correto: "Ministério da Educação"
  - ❌ Exemplo incorreto: "mec"
- [ ] Se aparecer sigla ao invés do nome, FALHOU

### 8. Conteúdo da Notícia - Complexidade com Emoji ✅
**Verificar no conteúdo principal:**

- [ ] Campo "Complexidade" mostra emoji + texto:
  - "🟢 clara" OU
  - "🟡 moderada" OU
  - "🔴 dificil"

### 9. Conteúdo da Notícia - Unique ID NÃO Visível ✅
**Verificar no conteúdo principal:**

- [ ] NÃO aparece campo "ID:" ou "unique_id"
- [ ] Se aparecer unique_id, FALHOU

### 10. Classificação Hierárquica L1→L2→L3 ✅ **TESTE CRÍTICO**
**Ação:** Testar a seleção hierárquica

**Passo 1 - L1:**
- [ ] Seção "🏷️ Classificação Temática" está visível
- [ ] Campo "Tema (L1)" tem tooltip de ajuda
- [ ] Selecionar um tema L1 (ex: "01 - Economia e Finanças")

**Passo 2 - L2 (CRÍTICO):**
- [ ] **IMEDIATAMENTE** após selecionar L1, campo "Subtema (L2)" aparece
- [ ] Campo L2 mostra apenas subtemas do L1 selecionado
- [ ] Campo L2 tem tooltip de ajuda
- [ ] Selecionar um subtema L2 (ex: "01.01 - Política Econômica")

**Passo 3 - L3:**
- [ ] **IMEDIATAMENTE** após selecionar L2, campo "Categoria (L3)" aparece
- [ ] Campo L3 mostra apenas categorias do L2 selecionado
- [ ] Campo L3 tem tooltip de ajuda

**Se L2 NÃO aparecer após selecionar L1, o bug CRÍTICO ainda existe!**

### 11. Formulário de Avaliação ✅
**Verificar campos do formulário:**

- [ ] Seção "📊 Avaliação da Classificação" está visível
- [ ] Slider "Confiança na Classificação" está presente
  - Opções: baixa / media / alta
  - Tem tooltip de ajuda
- [ ] Campo "Observações (opcional)" está presente
  - Tem placeholder: "Casos ambíguos, dúvidas, comentários..."
  - Tem tooltip de ajuda

### 12. Botões de Ação ✅
**Verificar botões:**

- [ ] Botão "💾 Salvar Anotação" (azul, destaque)
- [ ] Botão "⏭️ Pular"

### 13. Validação de Salvamento ✅
**Ação:** Tentar salvar SEM selecionar L1

**Resultado esperado:**
- [ ] Mensagem de erro: "⚠️ Selecione pelo menos o Tema (L1)"

### 14. Salvamento Bem-sucedido ✅
**Ação:** Selecionar L1, L2, L3, confiança e clicar "Salvar Anotação"

**Resultado esperado:**
- [ ] Mensagem de sucesso: "✅ Anotação salva!"
- [ ] App navega automaticamente para próxima notícia
- [ ] Métricas de progresso atualizam

### 15. Ground Truth - Código E Label ✅
**Verificar no final da página:**

- [ ] Expansor "🔍 Ver Classificação Original (Ground Truth)" está presente
- [ ] Clicar para expandir
- [ ] **VERIFICAR FORMATO:**
  - ✅ Exemplo correto: "L1: `01` - Economia e Finanças"
  - ❌ Exemplo incorreto: "L1: `01`" (sem label)
- [ ] Se tiver L2 original: "L2: `01.01` - Política Econômica"
- [ ] Se tiver L3 original: "L3: `01.01.01` - Política Fiscal"

### 16. Navegação entre Notícias ✅
**Verificar botões de navegação no topo:**

- [ ] Contador central: "Notícia X de Y"
- [ ] Botão "⬅️ Anterior" funciona
- [ ] Botão "Próxima ➡️" funciona
- [ ] Ao navegar, os campos L1/L2/L3 resetam (ou carregam anotação existente)

### 17. Voltar para Home ✅
**Ação:** Clicar em "🏠 Voltar para Home" na sidebar

**Resultado esperado:**
- [ ] App retorna para página inicial
- [ ] Nome do anotador permanece preenchido (persistência)

### 18. Filtros Funcionando ✅
**Testar filtros na sidebar:**

**Filtro de Status:**
- [ ] "Todas" - mostra todas as notícias
- [ ] "Pendentes" - mostra apenas não anotadas
- [ ] "Anotadas" - mostra apenas já anotadas

**Filtro de Complexidade:**
- [ ] "Todas" - mostra todas
- [ ] "clara" (com 🟢) - filtra apenas claras
- [ ] "moderada" (com 🟡) - filtra apenas moderadas
- [ ] "dificil" (com 🔴) - filtra apenas difíceis

---

## 🐛 Bugs Conhecidos

### ✅ RESOLVIDOS:
1. ~~L1 não mostrava campo L2~~ - CORRIGIDO (movido para fora do form)
2. ~~Agência mostrava sigla~~ - CORRIGIDO (carrega agencies.yaml)
3. ~~Sem emoji de complexidade~~ - CORRIGIDO (🟢🟡🔴)
4. ~~Unique_id visível~~ - CORRIGIDO (removido)
5. ~~Ground truth sem label~~ - CORRIGIDO (mostra código + label)
6. ~~Sem home page~~ - CORRIGIDO (home completa implementada)

---

## 📊 Resultado Final

**Testes Passados:** ____ / 18

**Status Geral:**
- [ ] ✅ Todos os testes passaram
- [ ] ⚠️ Alguns testes falharam (especificar quais)
- [ ] ❌ Muitos testes falharam

**Observações:**
_____________________________________________________
_____________________________________________________
_____________________________________________________

---

## 🚀 Próximos Passos

Se todos os testes passarem:
1. ✅ App está pronto para uso em anotação
2. ✅ Pode ser testado com usuários reais
3. ✅ Próximo: preparar deploy no GCP

Se houver falhas:
1. Documentar bugs encontrados neste arquivo
2. Reportar para desenvolvimento
3. Priorizar correções críticas (especialmente reatividade L1→L2→L3)
