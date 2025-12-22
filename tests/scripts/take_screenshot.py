#!/usr/bin/env python3
"""
Script para capturar screenshot do app usando Playwright
"""
from playwright.sync_api import sync_playwright
import time

def take_screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Ir para o modo direto (pula home)
        print("📱 Navegando para o app...")
        page.goto("http://localhost:8501?direct=true")

        # Aguardar carregamento
        print("⏳ Aguardando carregamento...")
        page.wait_for_selector("[data-testid='stAppViewContainer']", timeout=10000)
        time.sleep(4)  # Aguardar renderização completa

        # Capturar screenshot
        screenshot_path = "/tmp/streamlit_annotation_app.png"
        print(f"📸 Capturando screenshot...")
        page.screenshot(path=screenshot_path, full_page=True)

        print(f"✅ Screenshot salvo em: {screenshot_path}")

        browser.close()
        return screenshot_path

if __name__ == "__main__":
    path = take_screenshot()
    print(f"\nPara visualizar: open {path}")
