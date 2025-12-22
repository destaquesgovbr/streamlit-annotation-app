#!/usr/bin/env python3
"""
Script para testar layout em 2 colunas do app de anotação.
"""
from playwright.sync_api import sync_playwright
import time

def test_columns_layout():
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

        # Tirar screenshot do layout em colunas
        screenshot_path = "/tmp/test_layout_columns.png"
        print(f"\n📸 Capturando screenshot do layout em colunas...")
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Screenshot salvo em: {screenshot_path}")

        # Verificar se as colunas estão presentes
        print("\n🔍 Verificando estrutura de colunas...")

        # Procurar por elementos de coluna do Streamlit
        columns = page.locator("[data-testid='column']")
        column_count = columns.count()
        print(f"   Colunas encontradas: {column_count}")

        if column_count >= 2:
            print("   ✅ Layout em colunas detectado!")
        else:
            print("   ⚠️  Layout em colunas não detectado claramente")

        # Verificar se notícia e formulário estão visíveis simultaneamente
        print("\n🔍 Verificando elementos visíveis...")

        # Verificar título da notícia
        news_title = page.locator("h2")
        if news_title.is_visible():
            print("   ✅ Título da notícia visível")

        # Verificar formulário de classificação
        classification_title = page.locator("text=🏷️ Classificação Temática")
        if classification_title.is_visible():
            print("   ✅ Formulário de classificação visível")

        # Verificar se ambos estão visíveis ao mesmo tempo
        if news_title.is_visible() and classification_title.is_visible():
            print("   ✅ Notícia e formulário visíveis simultaneamente!")

        print(f"\n📂 Screenshot salvo em: {screenshot_path}")

        # Manter navegador aberto por 5 segundos para inspeção visual
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    print("🧪 Teste de Layout em 2 Colunas\n")
    print("="*60)
    test_columns_layout()
    print("="*60)
    print("\n✅ Teste concluído!")
