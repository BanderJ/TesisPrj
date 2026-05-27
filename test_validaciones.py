import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Navegar a la página de registro
        await page.goto('http://localhost:8000/registro', wait_until='networkidle')

        # Esperar a que carguen los selects
        await page.wait_for_selector('#tipoDocumento')
        await page.wait_for_selector('#pesoTotal')

        print("OK: Pagina de registro cargada")

        # === PRUEBA 1: Peso de muestra > Peso total ===
        print("\n=== Prueba 1: Peso muestra (1200) > Peso total (1 kg = 1000 gr) ===")
        await page.fill('#pesoTotal', '1')
        await page.fill('#pesoMuestra', '1200')
        await page.wait_for_timeout(500)

        # Capturar el hint
        hint1_text = await page.locator('#pesoMuestraHint').text_content()
        print(f"Hint: {hint1_text}")
        if "No puede superar" in hint1_text:
            print("PASS: Validacion correcta")
        else:
            print("FAIL: Hint no es el esperado")

        # Tomar screenshot
        await page.screenshot(path='d:\\tmp\\test1.png')

        # === PRUEBA 2: Peso trillado = Peso muestra ===
        print("\n=== Prueba 2: Peso trillado = Peso muestra ===")
        await page.fill('#pesoMuestra', '500')
        await page.fill('#pesoTrillado', '500')
        await page.wait_for_timeout(500)

        hint2_text = await page.locator('#pesoTrilladoHint').text_content()
        print(f"Hint: {hint2_text}")
        if "diferente" in hint2_text:
            print("PASS: Validacion correcta")
        else:
            print("FAIL: Hint no es el esperado")

        await page.screenshot(path='d:\\tmp\\test2.png')

        # === PRUEBA 3: Valores validos ===
        print("\n=== Prueba 3: Valores validos ===")
        await page.fill('#pesoMuestra', '800')
        await page.fill('#pesoTrillado', '600')
        await page.wait_for_timeout(500)

        hint3_text = await page.locator('#pesoTrilladoHint').text_content()
        print(f"Hint: {hint3_text}")
        if "Maximo" in hint3_text or not "error" in hint3_text.lower():
            print("PASS: Sin errores")
        else:
            print("FAIL: Hint muestra error")

        await page.screenshot(path='d:\\tmp\\test3.png')

        await browser.close()
        print("\nOK: Pruebas completadas")

asyncio.run(test())
