"""Playwright automated screenshots for Project 4: AI Text Summarizer
Complete workflow: home → input key → paste text → summarize → view result
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "http://localhost:8505"
API_KEY = "sk-6f8d2237dc1446caa4d656d4f0d360d8"
OUT = Path(__file__).resolve().parent.parent / "screenshots" / "p4_summarizer"
OUT.mkdir(parents=True, exist_ok=True)

SAMPLE_TEXT = """Artificial intelligence (AI) is transforming the way we live and work. From virtual assistants like Siri and Alexa to self-driving cars and medical diagnosis systems, AI technologies are becoming increasingly integrated into our daily lives. Machine learning, a subset of AI, enables computers to learn from data without being explicitly programmed. Deep learning, which uses neural networks with many layers, has achieved remarkable results in image recognition, natural language processing, and game playing. However, the rapid advancement of AI also raises important ethical questions about privacy, job displacement, and the potential for bias in automated decision-making systems. As AI continues to evolve, it is crucial that we develop frameworks for responsible AI development that balance innovation with societal well-being. Researchers and policymakers around the world are working together to establish guidelines and regulations that ensure AI benefits humanity while minimizing potential risks. The future of AI holds tremendous promise, but it requires careful stewardship to realize its full potential for good."""


async def shot(page, name, full=False):
    p = str(OUT / f"{name}.png")
    await page.screenshot(path=p, full_page=full)
    print(f"  -> {name}.png")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        # 1. Home page
        print("1. Home page...")
        await page.goto(BASE, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)
        await shot(page, "p4_01_home")

        # 2. Sidebar
        print("2. Sidebar...")
        try:
            toggle = page.locator('[data-testid="stSidebarCollapsedControl"]')
            if await toggle.is_visible(timeout=2000):
                await toggle.click()
                await asyncio.sleep(1)
        except:
            pass
        await shot(page, "p4_02_sidebar")

        # 3. Input API Key
        print("3. Input API Key...")
        key_input = page.locator('input[type="password"]')
        await key_input.fill(API_KEY)
        await asyncio.sleep(1)
        await shot(page, "p4_03_apikey")

        # 4. Paste text
        print("4. Paste text...")
        textarea = page.locator("textarea").first
        await textarea.fill(SAMPLE_TEXT)
        await asyncio.sleep(1)
        await shot(page, "p4_04_text_input")
        await shot(page, "p4_04_text_input_full", full=True)

        # 5. Click Summarize
        print("5. Summarize...")
        btn = page.locator('[data-testid="stBaseButton-primary"]')
        await btn.click()
        # Wait for streaming to complete
        await asyncio.sleep(20)
        await shot(page, "p4_05_result")
        await shot(page, "p4_05_result_full", full=True)

        # 6. Scroll down to see compression stats
        print("6. Scroll to stats...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        await shot(page, "p4_06_stats")

        # 7. Change settings - select "Short" length
        print("7. Change settings...")
        try:
            # Click on slider to change summary length
            slider = page.locator('[data-testid="stSlider"]')
            if await slider.is_visible(timeout=2000):
                await shot(page, "p4_07_settings")
        except:
            pass

        await browser.close()
    print("Done! All screenshots saved.")


asyncio.run(main())
