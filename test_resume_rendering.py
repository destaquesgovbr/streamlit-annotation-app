#!/usr/bin/env python3
"""
Script para verificar se o resumo está sendo renderizado corretamente.

Navega para a primeira notícia (index 0) que sabemos que tem resumo.
"""
from playwright.sync_api import sync_playwright
import time

def test_resume_rendering():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        # Ir para o app no modo direto
        print("📱 Navegando para o app...")
        page.goto("http://localhost:8501?direct=true")

        # Aguardar carregamento
        print("⏳ Aguardando carregamento...")
        page.wait_for_selector("[data-testid='stAppViewContainer']", timeout=10000)
        time.sleep(3)

        # Clicar no botão "Anterior" várias vezes para voltar à primeira notícia (index 0)
        print("⬅️ Navegando para a primeira notícia (index 0)...")
        for _ in range(10):  # Clicar até 10 vezes para garantir que chegamos no início
            anterior_btn = page.locator("button:has-text('⬅️ Anterior')")
            if anterior_btn.is_visible() and not anterior_btn.is_disabled():
                anterior_btn.click()
                time.sleep(1.5)
            else:
                print(f"   Chegou na primeira notícia!")
                break

        # Aguardar render
        time.sleep(2)

        # Verificar qual notícia estamos vendo
        counter = page.locator("text=/Notícia \\d+ de/")
        if counter.is_visible():
            counter_text = counter.inner_text()
            print(f"📍 Posição atual: {counter_text}")

        # Verificar se o container do resumo está visível
        print("\n🔍 Verificando container do resumo...")

        # Procurar pelo label "📝 Resumo"
        resume_label = page.locator("text=📝 Resumo")

        if resume_label.is_visible():
            print("✅ Label '📝 Resumo' ENCONTRADO!")
        else:
            print("❌ Label '📝 Resumo' NÃO ENCONTRADO!")

        # Procurar por container com borda
        resume_container = page.locator("[data-testid='stVerticalBlockBorderWrapper']").first
        if resume_container.is_visible():
            print("✅ Container com borda ENCONTRADO!")
        else:
            print("❌ Container com borda NÃO ENCONTRADO!")

        # Tirar screenshot
        screenshot_path = "/tmp/test_resume_first_news.png"
        print(f"\n📸 Capturando screenshot...")
        page.screenshot(path=screenshot_path)
        print(f"✅ Screenshot salvo em: {screenshot_path}")

        # Pegar HTML para análise
        print("\n📄 Extraindo HTML da página...")
        html_content = page.content()

        # Verificar se "📝 Resumo" está no HTML
        if "📝 Resumo" in html_content:
            print("✅ Texto '📝 Resumo' está no HTML")
        else:
            print("❌ Texto '📝 Resumo' NÃO está no HTML")

        # Verificar se há containers com borda
        if "stVerticalBlockBorderWrapper" in html_content:
            print("✅ Container com borda está no HTML")
        else:
            print("❌ Container com borda NÃO está no HTML")

        # Salvar HTML para inspeção
        html_path = "/tmp/test_resume_page.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML salvo em: {html_path}")

        print(f"\n📂 Arquivos gerados:")
        print(f"   Screenshot: {screenshot_path}")
        print(f"   HTML: {html_path}")

        # Manter navegador aberto por 3 segundos
        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    print("🧪 Teste de Renderização do Resumo\n")
    print("="*60)
    test_resume_rendering()
    print("="*60)
    print("\n✅ Teste concluído!")
