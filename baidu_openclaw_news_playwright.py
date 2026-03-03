from playwright.sync_api import sync_playwright

print("Hello, trigger workflow!")
def fetch_openclaw_news(limit: int = 2) -> list[dict[str, str]]:
    """Search `openclaw` on Baidu News and return top news results."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
       # browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        page.goto("https://www.baidu.com", wait_until="domcontentloaded")
        page.fill("#kw", "openclaw")
        page.click("#su")

        page.wait_for_load_state("domcontentloaded")
        page.get_by_role("link", name="新闻").first.click()
        page.wait_for_load_state("domcontentloaded")

        page.wait_for_selector("h3 a", timeout=15000)
        links = page.locator("h3 a")

        news: list[dict[str, str]] = []
        for i in range(min(limit, links.count())):
            item = links.nth(i)
            news.append(
                {
                    "title": item.inner_text().strip(),
                    "url": item.get_attribute("href") or "",
                }
            )

        browser.close()
        return news


if __name__ == "__main__":
    results = fetch_openclaw_news(limit=2)
    for idx, item in enumerate(results, start=1):
        print(f"{idx}. {item['title']}")
        print(f"   {item['url']}")
