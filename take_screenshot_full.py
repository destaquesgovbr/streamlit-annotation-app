#!/usr/bin/env python3
"""
Script para capturar screenshot completo incluindo a seção de classificação
"""
from playwright.sync_api import sync_playwright
import time

def take_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        # Ir para o modo direto (pula home)
        print("📱 Navegando para o app...")
        page.goto("http://localhost:8501?direct=true")

        # Aguardar carregamento
        print("⏳ Aguardando carregamento...")
        page.wait_for_selector("[data-testid='stAppViewContainer']", timeout=10000)
        time.sleep(4)  # Aguardar renderização completa

        # Screenshot 1: Topo (notícia)
        screenshot1 = "/tmp/streamlit_1_noticia.png"
        print(f"📸 Capturando screenshot 1 (topo)...")
        page.screenshot(path=screenshot1)
        print(f"✅ Screenshot 1 salvo em: {screenshot1}")

        # Scroll para baixo para ver o formulário
        print("⬇️ Fazendo scroll para ver formulário...")
        page.evaluate("window.scrollTo(0, 600)")
        time.sleep(1)

        # Screenshot 2: Formulário de classificação
        screenshot2 = "/tmp/streamlit_2_formulario.png"
        print(f"📸 Capturando screenshot 2 (formulário)...")
        page.screenshot(path=screenshot2)
        print(f"✅ Screenshot 2 salvo em: {screenshot2}")

        # Screenshot 3: Full page
        screenshot3 = "/tmp/streamlit_3_full.png"
        print(f"📸 Capturando screenshot 3 (página completa)...")
        page.screenshot(path=screenshot3, full_page=True)
        print(f"✅ Screenshot 3 salvo em: {screenshot3}")

        browser.close()
        return screenshot1, screenshot2, screenshot3

if __name__ == "__main__":
    s1, s2, s3 = take_screenshots()
    print(f"\n📂 Screenshots salvos:")
    print(f"   1. Topo: {s1}")
    print(f"   2. Formulário: {s2}")
    print(f"   3. Página completa: {s3}")
