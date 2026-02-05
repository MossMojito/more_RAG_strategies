import asyncio
import os
import re
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from ..config import AVAILABLE_SPORTS

class SportsCrawler:
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
        self.browser_config = BrowserConfig(headless=True, verbose=False)
        self.crawl_config = CrawlerRunConfig(
            js_code=[f"""
                if (document.querySelector('input[name="username"]')) {{
                    document.querySelector('input[name="username"]').value = '{self.username}';
                    document.querySelector('input[name="password"]').value = '{self.password}';
                    document.querySelector('form').submit();
                    await new Promise(r => setTimeout(r, 5000));
                }}
            """] if username and password else [],
            wait_until="networkidle",
            page_timeout=15000,
            delay_before_return_html=6.0
        )

    async def scrape_urls(self, urls: dict):
        """
        Scrape a dictionary of {name: url}.
        Returns: {name: {"raw_md": str, "img_urls": list, "html": str}}
        """
        all_data = {}
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for name, url in urls.items():
                print(f"🕷️ Crawling {name}...")
                # Use session_id to maintain the logged-in state if needed
                result = await crawler.arun(url=url, config=self.crawl_config, session_id="sports_session")

                if result.success:
                    # Extract image URLs
                    imgs = list(set(re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', result.html)))
                    
                    all_data[name] = {
                        "raw_md": result.markdown,
                        "img_urls": imgs,
                        "html": result.html
                    }
                    print(f"   ✅ Success: {len(result.markdown)} chars, {len(imgs)} images")
                else:
                    print(f"   ❌ Failed to crawl {name}")
        
        return all_data

# Example usage function
async def run_crawler(urlsfile):
    crawler = SportsCrawler()
    return await crawler.scrape_urls(urlsfile)
