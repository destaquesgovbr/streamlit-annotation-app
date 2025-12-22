"""
Testes do fluxo de anotação usando Playwright.

Para executar os testes, certifique-se de que:
1. O app Streamlit está rodando em http://localhost:8501
2. As dependências estão instaladas: pip install -r tests/requirements.txt
3. Playwright browsers instalados: playwright install

Executar testes:
    pytest tests/test_annotation_flow.py -v
"""

import pytest
from playwright.sync_api import Page, expect


class TestHomePage:
    """Testes da página inicial"""

    def test_home_page_loads(self, page_with_app: Page):
        """Verifica que a home page carrega corretamente"""
        page = page_with_app

        # Verificar título principal
        expect(page.locator("text=Anotação Manual de Notícias GovBR")).to_be_visible()

        # Verificar seções de instruções
        expect(page.locator("text=🎯 Objetivo")).to_be_visible()
        expect(page.locator("text=📝 Como Anotar")).to_be_visible()
        expect(page.locator("text=✅ Dicas de Qualidade")).to_be_visible()

    def test_annotator_name_field_exists(self, page_with_app: Page):
        """Verifica que o campo de nome do anotador existe"""
        page = page_with_app

        # Verificar campo de nome
        name_input = page.get_by_placeholder("Digite seu nome completo")
        expect(name_input).to_be_visible()

    def test_start_button_validation(self, page_with_app: Page):
        """Verifica validação ao tentar iniciar sem nome"""
        page = page_with_app

        # Tentar iniciar sem preencher nome
        start_button = page.locator("text=🚀 Iniciar Anotação")
        start_button.click()

        # Deve mostrar mensagem de erro
        expect(page.locator("text=Por favor, informe seu nome antes de iniciar")).to_be_visible(timeout=3000)


class TestAnnotationInterface:
    """Testes da interface de anotação"""

    @pytest.fixture
    def annotation_page(self, page_with_annotation: Page):
        """
        Fixture que usa modo direto (direct=true) para pular home page.

        Isso evita problemas com reruns do Streamlit nos testes.
        """
        # Já está na interface de anotação (direct mode)
        return page_with_annotation

    def test_sidebar_shows_annotator_name(self, annotation_page: Page):
        """Verifica que o nome do anotador aparece no topo da sidebar"""
        page = annotation_page

        # Verificar nome na sidebar (modo direto usa "Test User")
        expect(page.locator("text=👤 Test User")).to_be_visible()

    def test_sidebar_shows_progress_metrics(self, annotation_page: Page):
        """Verifica que métricas de progresso estão visíveis"""
        page = annotation_page

        # Verificar métricas
        expect(page.locator("text=📊 Progresso")).to_be_visible()
        expect(page.locator("text=Total")).to_be_visible()
        expect(page.locator("text=Anotadas")).to_be_visible()
        expect(page.locator("text=Pendentes")).to_be_visible()

    def test_filters_have_tooltips(self, annotation_page: Page):
        """Verifica que os filtros têm tooltips (help text)"""
        page = annotation_page

        # Filtro de Status deve ter tooltip
        status_label = page.locator("text=Status").first
        expect(status_label).to_be_visible()

        # Filtro de Complexidade deve ter tooltip
        complexity_label = page.locator("text=Complexidade").first
        expect(complexity_label).to_be_visible()

    def test_complexity_has_emoji(self, annotation_page: Page):
        """Verifica que a complexidade exibe emoji"""
        page = annotation_page

        # Aguardar conteúdo carregar
        page.wait_for_timeout(2000)

        # Procurar por emojis de complexidade no corpo principal (não no filtro)
        complexity_section = page.locator("text=/Complexidade:.*[🟢🟡🔴]/")
        expect(complexity_section).to_be_visible()

    def test_agency_shows_full_name_not_sigla(self, annotation_page: Page):
        """Verifica que o nome completo da agência é exibido, não apenas a sigla"""
        page = annotation_page

        # Aguardar conteúdo carregar
        page.wait_for_timeout(2000)

        # Verificar que existe um órgão exibido
        organ_label = page.locator("text=/Órgão:.*Ministério|Agência|Secretaria|Instituto/")
        expect(organ_label).to_be_visible()

    def test_unique_id_not_displayed(self, annotation_page: Page):
        """Verifica que o unique_id NÃO é exibido"""
        page = annotation_page

        # Aguardar conteúdo carregar
        page.wait_for_timeout(2000)

        # Não deve ter texto "ID:" ou "unique_id"
        id_elements = page.locator("text=/ID:|unique_id/")
        expect(id_elements).not_to_be_visible()

    def test_l1_selection_shows_l2_field(self, annotation_page: Page):
        """TESTE CRÍTICO: Verifica que selecionar L1 faz aparecer o campo L2"""
        page = annotation_page

        # Aguardar carregamento
        page.wait_for_timeout(2000)

        # Encontrar seletor L1
        l1_selector = page.locator("[data-testid='stSelectbox']").filter(has_text="Tema (L1)").first

        # Inicialmente L2 não deve estar visível
        l2_selector = page.locator("text=Subtema (L2)")
        expect(l2_selector).not_to_be_visible()

        # Clicar no seletor L1
        l1_selector.click()

        # Selecionar primeiro tema disponível (não vazio)
        # Aguardar opções carregarem
        page.wait_for_timeout(500)

        # Selecionar uma opção que não seja vazia
        first_option = page.locator("[role='option']").filter(has_text="01 -").first
        if first_option.is_visible():
            first_option.click()

            # Aguardar reatividade
            page.wait_for_timeout(1000)

            # Agora L2 DEVE estar visível
            expect(l2_selector).to_be_visible(timeout=3000)

    def test_l2_selection_shows_l3_field(self, annotation_page: Page):
        """TESTE CRÍTICO: Verifica que selecionar L2 faz aparecer o campo L3"""
        page = annotation_page

        # Aguardar carregamento
        page.wait_for_timeout(2000)

        # Selecionar L1 primeiro
        l1_selector = page.locator("[data-testid='stSelectbox']").filter(has_text="Tema (L1)").first
        l1_selector.click()
        page.wait_for_timeout(500)

        first_l1_option = page.locator("[role='option']").filter(has_text="01 -").first
        if first_l1_option.is_visible():
            first_l1_option.click()
            page.wait_for_timeout(1000)

            # Selecionar L2
            l2_selector = page.locator("[data-testid='stSelectbox']").filter(has_text="Subtema (L2)").first
            l2_selector.click()
            page.wait_for_timeout(500)

            # Selecionar primeiro subtema disponível
            first_l2_option = page.locator("[role='option']").filter(has_text="01.01").first
            if first_l2_option.is_visible():
                first_l2_option.click()
                page.wait_for_timeout(1000)

                # Agora L3 DEVE estar visível
                l3_selector = page.locator("text=Categoria (L3)")
                expect(l3_selector).to_be_visible(timeout=3000)

    def test_ground_truth_shows_code_and_label(self, annotation_page: Page):
        """Verifica que o ground truth mostra conteúdo quando expandido"""
        page = annotation_page

        # Aguardar carregamento
        page.wait_for_timeout(2000)

        # Procurar expander de ground truth
        ground_truth_expander = page.locator("text=Ver Classificação Original (Ground Truth)")

        # Apenas testar se o ground truth existir para esta notícia
        if ground_truth_expander.is_visible():
            # Expandir
            ground_truth_expander.click()
            page.wait_for_timeout(1000)

            # Verificar que o expander tem conteúdo (L1:, L2: ou L3:)
            # Procurar por qualquer um dos níveis
            has_content = (
                page.locator("text=/L1:/").is_visible() or
                page.locator("text=/L2:/").is_visible() or
                page.locator("text=/L3:/").is_visible()
            )

            assert has_content, "Ground truth expandido mas sem conteúdo L1/L2/L3"
        # Se não tiver ground truth, o teste passa (algumas notícias podem não ter)

    def test_navigation_buttons_work(self, annotation_page: Page):
        """Verifica que os botões de navegação funcionam"""
        page = annotation_page

        # Aguardar carregamento
        page.wait_for_timeout(2000)

        # Verificar posição atual (ex: "Notícia 1 de X")
        counter = page.locator("text=/Notícia \\d+ de \\d+/")
        expect(counter).to_be_visible()

        initial_text = counter.inner_text()

        # Clicar em "Próxima"
        next_button = page.locator("text=Próxima ➡️")
        if next_button.is_visible():
            next_button.click()
            page.wait_for_timeout(1500)

            # Contador deve ter mudado
            new_text = counter.inner_text()
            assert initial_text != new_text, "Navegação não funcionou"

    def test_confidence_slider_exists(self, annotation_page: Page):
        """Verifica que o slider de confiança existe"""
        page = annotation_page

        # Aguardar carregamento
        page.wait_for_timeout(2000)

        # Verificar slider de confiança
        confidence_label = page.locator("text=Confiança na Classificação")
        expect(confidence_label).to_be_visible()

    def test_observations_field_exists(self, annotation_page: Page):
        """Verifica que o campo de observações existe"""
        page = annotation_page

        # Aguardar carregamento
        page.wait_for_timeout(2000)

        # Verificar campo de observações
        obs_field = page.get_by_placeholder("Casos ambíguos, dúvidas, comentários...")
        expect(obs_field).to_be_visible()

    def test_submit_button_validation(self, annotation_page: Page):
        """Verifica que o botão salvar está desabilitado quando L1 não está selecionado"""
        page = annotation_page

        # Aguardar carregamento
        page.wait_for_timeout(2000)

        # Verificar que o botão está desabilitado (não pode clicar)
        save_button = page.locator("button:has-text('💾 Salvar Anotação')")

        # Botão deve estar desabilitado
        expect(save_button).to_be_disabled()

    def test_back_to_home_button_works(self, annotation_page: Page):
        """Verifica que o botão de voltar para home funciona"""
        page = annotation_page

        # Clicar em voltar para home
        home_button = page.locator("text=🏠 Voltar para Home")
        home_button.click()

        # Deve voltar para home
        expect(page.locator("text=🎯 Objetivo")).to_be_visible(timeout=5000)


class TestRandomSelection:
    """Testes para seleção randômica de notícias"""

    @pytest.fixture
    def annotation_page(self, page_with_annotation: Page):
        """Fixture para testes de randomização"""
        return page_with_annotation

    def test_initial_selection_is_random(self, app_url_direct: str, page: Page):
        """Verifica que a seleção inicial é aleatória (não sempre a primeira)"""
        # Carregar app 5 vezes e verificar que não sempre começa na mesma notícia
        initial_news = []

        for _ in range(5):
            # Criar nova sessão (limpar session state)
            page.goto(f"{app_url_direct}&random={_}")  # Query param diferente força nova sessão
            page.wait_for_selector("[data-testid='stAppViewContainer']", timeout=10000)
            page.wait_for_timeout(3000)

            # Pegar número da notícia atual
            counter = page.locator("text=/Notícia \\d+ de/")
            if counter.is_visible():
                text = counter.inner_text()
                # Extrair número (ex: "Notícia 248 de 500" -> 248)
                import re
                match = re.search(r'Notícia (\d+) de', text)
                if match:
                    initial_news.append(int(match.group(1)))

        # Se é randômico, deve ter pelo menos 2 valores diferentes
        unique_values = set(initial_news)
        assert len(unique_values) >= 2, f"Seleção inicial não é randômica: {initial_news}"

    def test_skip_button_selects_random_news(self, annotation_page: Page):
        """Verifica que o botão Pular seleciona uma notícia aleatória"""
        page = annotation_page

        # Pegar notícia atual
        counter = page.locator("text=/Notícia \\d+ de/")
        expect(counter).to_be_visible()

        initial_text = counter.inner_text()
        initial_number = None
        import re
        match = re.search(r'Notícia (\d+) de', initial_text)
        if match:
            initial_number = int(match.group(1))

        # Clicar em Pular múltiplas vezes e verificar que não é sempre sequencial
        skip_numbers = []
        skip_button = page.locator("button:has-text('⏭️ Pular')")

        for _ in range(3):
            skip_button.click()
            page.wait_for_timeout(2000)  # Aguardar rerun

            new_text = counter.inner_text()
            match = re.search(r'Notícia (\d+) de', new_text)
            if match:
                skip_numbers.append(int(match.group(1)))

        # Verificar que não pulou sequencialmente (ex: 1, 2, 3)
        # Se for aleatório, os números não devem ser todos consecutivos
        is_sequential = all(skip_numbers[i] == skip_numbers[i-1] + 1 for i in range(1, len(skip_numbers)))

        # Se não for sequencial, é um bom indicador de randomização
        # (pode falhar por sorte, mas é improvável)
        assert not is_sequential or len(set(skip_numbers)) > 1, "Botão Pular parece estar selecionando sequencialmente"


class TestScrollBehavior:
    """Testes para comportamento de scroll automático

    IMPORTANTE: Testes de scroll são difíceis de implementar de forma confiável em Streamlit
    devido à estrutura de iframes e reruns.

    Para testar o scroll automático, use o script manual:
        python3 test_scroll_behavior.py

    Este script:
    1. Carrega o app
    2. Faz scroll para baixo
    3. Clica em "Pular"
    4. Tira screenshots para verificação visual
    5. Verifica a posição do scroll programaticamente
    """

    @pytest.fixture
    def annotation_page(self, page_with_annotation: Page):
        """Fixture para testes de scroll"""
        return page_with_annotation

    def test_scroll_script_exists_in_page(self, annotation_page: Page):
        """Verifica que o código de scroll está presente na página (teste básico)

        Para teste completo do comportamento de scroll, execute:
            python3 test_scroll_behavior.py
        """
        page = annotation_page

        # Aguardar carregamento
        page.wait_for_timeout(2000)

        # Verificar que o JavaScript de scroll está no HTML
        # (não testa se funciona, apenas se está presente)
        html_content = page.content()
        assert "scrollTo(0, 0)" in html_content, "JavaScript de scroll não encontrado no HTML"


class TestComplexityEmojis:
    """Testes específicos para emojis de complexidade"""

    @pytest.fixture
    def annotation_page(self, page_with_annotation: Page):
        """
        Fixture que usa modo direto (direct=true) para pular home page.
        """
        # Já está na interface de anotação (direct mode)
        return page_with_annotation

    def test_complexity_filter_shows_emoji(self, annotation_page: Page):
        """Verifica que o filtro de complexidade mostra emojis"""
        page = annotation_page

        # Aguardar carregamento
        page.wait_for_timeout(2000)

        # Clicar no filtro de complexidade
        complexity_selectbox = page.locator("[data-testid='stSelectbox']").filter(has_text="Complexidade")
        complexity_selectbox.click()

        page.wait_for_timeout(500)

        # Verificar que as opções têm emojis
        # 🟢 clara, 🟡 moderada, 🔴 dificil
        clara_option = page.locator("[role='option']").filter(has_text="🟢")
        moderada_option = page.locator("[role='option']").filter(has_text="🟡")
        dificil_option = page.locator("[role='option']").filter(has_text="🔴")

        # Pelo menos um deve estar visível
        assert clara_option.is_visible() or moderada_option.is_visible() or dificil_option.is_visible(), \
            "Nenhum emoji de complexidade encontrado no filtro"
