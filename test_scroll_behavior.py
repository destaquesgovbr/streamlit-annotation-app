#!/usr/bin/env python3
"""
Script para testar comportamento de scroll automático ao pular notícia.

O teste verifica se ao clicar em "Pular", a página volta para o topo automaticamente.

Passos:
1. Carregar app
2. Scroll para baixo
3. Clicar em "Pular"
4. Tirar screenshot para verificar se voltou ao topo

Para executar:
    python3 test_scroll_behavior.py

O screenshot será salvo em /tmp/test_scroll_after_skip.png
"""
from playwright.sync_api import sync_playwright
import time

def test_scroll_behavior():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visível para debug
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        # Ir para o modo direto (pula home)
        print("📱 Navegando para o app...")
        page.goto("http://localhost:8501?direct=true")

        # Aguardar carregamento
        print("⏳ Aguardando carregamento...")
        page.wait_for_selector("[data-testid='stAppViewContainer']", timeout=10000)
        time.sleep(3)  # Aguardar renderização completa

        # Screenshot 1: Estado inicial (topo)
        screenshot1 = "/tmp/test_scroll_1_initial_top.png"
        print(f"📸 Screenshot 1: Estado inicial (topo)")
        page.screenshot(path=screenshot1)
        print(f"   ✅ Salvo em: {screenshot1}")

        # Scroll para baixo (600px)
        print("\n⬇️ Fazendo scroll para baixo (600px)...")
        page.evaluate("window.scrollTo(0, 600)")
        time.sleep(1)

        # Screenshot 2: Após scroll (meio da página)
        screenshot2 = "/tmp/test_scroll_2_after_scroll_down.png"
        print(f"📸 Screenshot 2: Após scroll para baixo")
        page.screenshot(path=screenshot2)
        print(f"   ✅ Salvo em: {screenshot2}")

        # Clicar no botão Pular
        print("\n⏭️ Clicando no botão 'Pular'...")
        skip_button = page.locator("button:has-text('⏭️ Pular')")
        if skip_button.is_visible():
            skip_button.click()
            print("   ✅ Botão clicado")

            # Aguardar rerun do Streamlit
            time.sleep(3)

            # Screenshot 3: Após pular (deve estar no topo novamente)
            screenshot3 = "/tmp/test_scroll_3_after_skip.png"
            print(f"\n📸 Screenshot 3: Após clicar em Pular")
            page.screenshot(path=screenshot3)
            print(f"   ✅ Salvo em: {screenshot3}")

            # Verificar posição do scroll
            scroll_position = page.evaluate("window.scrollY")
            print(f"\n📊 Posição do scroll após pular: {scroll_position}px")

            if scroll_position == 0:
                print("✅ TESTE PASSOU: Scroll voltou ao topo!")
            else:
                print(f"⚠️ TESTE FALHOU: Scroll deveria estar em 0px, mas está em {scroll_position}px")
        else:
            print("❌ Botão 'Pular' não encontrado!")

        print("\n📂 Screenshots salvos para análise manual:")
        print(f"   1. Inicial (topo): {screenshot1}")
        print(f"   2. Após scroll: {screenshot2}")
        print(f"   3. Após pular: {screenshot3}")

        # Manter navegador aberto por 2 segundos para visualização
        time.sleep(2)
        browser.close()

if __name__ == "__main__":
    print("🧪 Teste de Scroll Automático\n")
    print("="*50)
    test_scroll_behavior()
    print("="*50)
    print("\n✅ Teste concluído. Verifique os screenshots em /tmp/")
