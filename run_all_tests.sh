#!/bin/bash
# Script para executar todos os testes do app de anotação
# Usage: ./run_all_tests.sh [--headed] [--slow]

set -e  # Parar em erros

# Ativar ambiente virtual do Poetry se existir
if [ -f "$HOME/Library/Caches/pypoetry/virtualenvs/govbr-news-ai-_H0Lmpg7-py3.13/bin/activate" ]; then
    source "$HOME/Library/Caches/pypoetry/virtualenvs/govbr-news-ai-_H0Lmpg7-py3.13/bin/activate"
fi

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se o app está rodando
echo -e "${BLUE}🔍 Verificando se app Streamlit está rodando...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | grep -q "200"; then
    echo -e "${GREEN}✅ App rodando em http://localhost:8501${NC}\n"
else
    echo -e "${YELLOW}⚠️  App não está rodando. Inicie com:${NC}"
    echo -e "${YELLOW}   ./run_local.sh${NC}\n"
    exit 1
fi

# Executar testes de integração
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📦 TESTES DE INTEGRAÇÃO${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${BLUE}1️⃣ Teste de Salvamento de Anotações${NC}"
python3 tests/integration/test_save_annotations.py
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Teste de salvamento passou!${NC}\n"
else
    echo -e "\n${RED}❌ Teste de salvamento falhou!${NC}\n"
    exit 1
fi

# Verificar se pytest está disponível
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}⚠️  pytest não encontrado. Pulando testes Playwright.${NC}"
    echo -e "${YELLOW}   Para instalar: pip install -r tests/requirements.txt${NC}\n"
    exit 0
fi

# Verificar se Playwright está instalado
if ! python3 -c "import playwright" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Playwright não encontrado. Pulando testes E2E.${NC}"
    echo -e "${YELLOW}   Para instalar:${NC}"
    echo -e "${YELLOW}   pip install -r tests/requirements.txt${NC}"
    echo -e "${YELLOW}   playwright install${NC}\n"
    exit 0
fi

# Executar testes Playwright (E2E)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🎭 TESTES E2E (PLAYWRIGHT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Construir argumentos do pytest baseado nos parâmetros
PYTEST_ARGS="-v"
if [[ "$*" == *"--headed"* ]]; then
    PYTEST_ARGS="$PYTEST_ARGS --headed"
    echo -e "${BLUE}🖥️  Modo headed ativado (navegador visível)${NC}"
fi

if [[ "$*" == *"--slow"* ]]; then
    PYTEST_ARGS="$PYTEST_ARGS --slowmo 1000"
    echo -e "${BLUE}🐌 Modo slow-mo ativado (1 segundo de delay)${NC}"
fi

echo ""

# Rodar testes Playwright
pytest tests/test_annotation_flow.py tests/e2e/ $PYTEST_ARGS

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Todos os testes Playwright passaram!${NC}\n"
else
    echo -e "\n${RED}❌ Alguns testes Playwright falharam!${NC}\n"
    exit 1
fi

# Resumo final
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 TODOS OS TESTES PASSARAM!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${GREEN}✅ Testes de integração: PASSOU${NC}"
echo -e "${GREEN}✅ Testes E2E (Playwright): PASSOU${NC}\n"

echo -e "${BLUE}📊 Resumo de Cobertura:${NC}"
echo -e "   • Salvamento de anotações: ✅"
echo -e "   • Preservação de códigos: ✅"
echo -e "   • Home page: ✅"
echo -e "   • Interface de anotação: ✅"
echo -e "   • Reatividade L1→L2→L3: ✅"
echo -e "   • Validações de formulário: ✅"
echo -e "   • Navegação: ✅"
echo -e "   • Filtros: ✅"
echo ""
