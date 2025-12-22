#!/usr/bin/env python3
"""
Teste para verificar comportamento do scroll ao passar da home para a tela de classificação.
Deveria mostrar os botões de Anterior e Próxima no topo da página.
"""
import sys
sys.path.insert(0, '/Users/nitai/Library/Caches/pypoetry/virtualenvs/govbr-news-ai-_H0Lmpg7-py3.13/lib/python3.13/site-packages')

from playwright.sync_api import sync_playwright
import time

def test_initial_scroll_position():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        print("🧪 Teste de Posição Inicial do Scroll\n")
        print("="*60)

        # 1. Ir para o app (tela home)
        print("\n1️⃣ Navegando para tela home...")
        page.goto("http://localhost:8501")
        page.wait_for_selector("[data-testid='stAppViewContainer']", timeout=10000)
        time.sleep(2)

        # Tirar screenshot da home
        print("   📸 Capturando tela home...")
        page.screenshot(path="/tmp/test_home.png")
        print("   ✅ Screenshot salvo: /tmp/test_home.png")

        # 2. Preencher nome do anotador
        print("\n2️⃣ Preenchendo nome do anotador...")
        name_input = page.locator("input[type='text']").first
        name_input.fill("Test User")
        time.sleep(0.5)

        # 3. Clicar no botão "Começar Anotação"
        print("\n3️⃣ Clicando em 'Começar Anotação'...")
        start_button = page.locator("button:has-text('Começar Anotação')")
        start_button.click()

        # Aguardar carregamento da tela de classificação
        print("   ⏳ Aguardando carregamento da tela de classificação...")
        time.sleep(3)

        # 4. Verificar posição do scroll
        print("\n4️⃣ Verificando posição do scroll...")
        scroll_position = page.evaluate("""
            () => {
                const mainSection = window.parent.document.querySelector('section.main');
                return mainSection ? mainSection.scrollTop : null;
            }
        """)
        print(f"   📍 Posição do scroll: {scroll_position}px")

        # 5. Verificar se os botões estão visíveis no viewport
        print("\n5️⃣ Verificando visibilidade dos botões...")

        anterior_btn = page.locator("button:has-text('⬅️ Anterior')")
        proxima_btn = page.locator("button:has-text('Próxima ➡️')")

        anterior_visible = anterior_btn.is_visible()
        proxima_visible = proxima_btn.is_visible()

        print(f"   Botão 'Anterior' visível: {'✅' if anterior_visible else '❌'}")
        print(f"   Botão 'Próxima' visível: {'✅' if proxima_visible else '❌'}")

        # 6. Verificar se os botões estão no viewport (sem precisar scroll)
        print("\n6️⃣ Verificando se botões estão no viewport...")

        if anterior_visible:
            anterior_box = anterior_btn.bounding_box()
            if anterior_box:
                print(f"   Posição do botão 'Anterior': y={anterior_box['y']}px")
                if anterior_box['y'] < 100:
                    print("   ✅ Botão 'Anterior' está no topo da página")
                else:
                    print(f"   ⚠️  Botão 'Anterior' está abaixo do topo (y={anterior_box['y']}px)")

        # 7. Tirar screenshot da tela inicial de classificação
        print("\n7️⃣ Capturando tela inicial de classificação...")
        page.screenshot(path="/tmp/test_initial_classification.png", full_page=True)
        print("   ✅ Screenshot salvo: /tmp/test_initial_classification.png")

        # 8. Pegar altura do viewport vs altura do conteúdo
        print("\n8️⃣ Verificando dimensões...")
        dimensions = page.evaluate("""
            () => {
                const mainSection = window.parent.document.querySelector('section.main');
                return {
                    viewportHeight: window.innerHeight,
                    scrollHeight: mainSection ? mainSection.scrollHeight : null,
                    clientHeight: mainSection ? mainSection.clientHeight : null,
                    scrollTop: mainSection ? mainSection.scrollTop : null
                };
            }
        """)
        print(f"   Altura viewport: {dimensions['viewportHeight']}px")
        print(f"   Altura conteúdo: {dimensions['scrollHeight']}px")
        print(f"   Altura visível: {dimensions['clientHeight']}px")
        print(f"   Posição scroll: {dimensions['scrollTop']}px")

        # 9. Verificar se há algum elemento com foco
        print("\n9️⃣ Verificando elemento com foco...")
        focused_element = page.evaluate("""
            () => {
                const focused = document.activeElement;
                if (focused) {
                    return {
                        tag: focused.tagName,
                        id: focused.id,
                        class: focused.className,
                        type: focused.type
                    };
                }
                return null;
            }
        """)
        if focused_element:
            print(f"   Elemento com foco: {focused_element}")
        else:
            print("   Nenhum elemento com foco")

        # Resultado
        print("\n" + "="*60)
        print("📊 RESULTADO:")
        print("="*60)

        if scroll_position == 0 and anterior_visible and proxima_visible:
            print("✅ TESTE PASSOU!")
            print("   - Scroll está no topo (0px)")
            print("   - Botões de navegação visíveis")
            success = True
        else:
            print("❌ TESTE FALHOU!")
            if scroll_position != 0:
                print(f"   - Scroll NÃO está no topo ({scroll_position}px)")
            if not anterior_visible or not proxima_visible:
                print("   - Botões de navegação NÃO visíveis")
            success = False

        print("\n📂 Screenshots salvos:")
        print("   - /tmp/test_home.png")
        print("   - /tmp/test_initial_classification.png")

        # Manter navegador aberto para inspeção
        print("\n⏸️  Mantendo navegador aberto por 10 segundos...")
        time.sleep(10)

        browser.close()
        return success

if __name__ == "__main__":
    success = test_initial_scroll_position()
    sys.exit(0 if success else 1)
