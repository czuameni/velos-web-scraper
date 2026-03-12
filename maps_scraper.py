import asyncio
import datetime

from playwright.async_api import async_playwright

from db import save_firm
from website_crawler import crawl_website


# ==============================
# LOAD REGIONS
# ==============================

def load_regions():

    with open("regions.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# ==============================
# LOAD KEYWORDS
# ==============================

def load_keywords():

    with open("keywords.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# ==============================
# MAIN SCRAPER
# ==============================

async def scrape_maps():

    REGIONS = load_regions()
    KEYWORDS = load_keywords()

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        for region in REGIONS:

            print(f"\n===== REGION: {region.upper()} =====")

            cities_file = f"cities_{region}.txt"

            with open(cities_file, "r", encoding="utf-8") as f:
                CITIES = [line.strip() for line in f if line.strip()]

            for city in CITIES:

                print(f"\nSearching city: {city}")

                for keyword in KEYWORDS:

                    print(f"\nKeyword: {keyword}")

                    url = f"https://www.google.com/maps/search/{keyword} {city} {region}"
                    await page.goto(url)

                    await page.wait_for_timeout(5000)

                    # ==============================
                    # SCROLL RESULTS
                    # ==============================

                    results_panel = page.locator('div[role="feed"]')

                    if await results_panel.count() == 0:
                        print("No feed panel — skipping")
                        continue

                    for _ in range(40):
                        await results_panel.evaluate(
                            "el => el.scrollBy(0, 10000)"
                        )
                        await page.wait_for_timeout(2000)

                    # ==============================
                    # COLLECT LISTINGS
                    # ==============================

                    listings = await page.locator(
                        'a[href*="/place"]'
                    ).all()

                    print(f"Found listings: {len(listings)}")

                    # ==============================
                    # SCRAPE EACH FIRM
                    # ==============================

                    for i, listing in enumerate(listings):

                        try:
                            print(f"Scraping firm {i+1}/{len(listings)}")

                            await listing.click(force=True)
                            await page.wait_for_timeout(4000)

                            # NAME
                            name_el = page.locator("h1.DUwDvf")

                            if await name_el.count() == 0:
                                continue

                            name = await name_el.inner_text()

                            # ADDRESS
                            address = None
                            addr_el = page.locator(
                                'button[data-item-id="address"]'
                            )

                            if await addr_el.count() > 0:
                                address = await addr_el.inner_text()

                            # PHONE
                            phone = None
                            phone_el = page.locator(
                                'button[data-item-id^="phone"]'
                            )

                            if await phone_el.count() > 0:
                                phone = await phone_el.inner_text()

                            # WEBSITE
                            website = None
                            web_el = page.locator(
                                'a[data-item-id="authority"]'
                            )

                            if await web_el.count() > 0:
                                website = await web_el.get_attribute("href")

                            # EMAIL CRAWL
                            email = None

                            if website:
                                emails = crawl_website(website)
                                if emails:
                                    email = emails[0]

                            # ==============================
                            # SAVE DATA
                            # ==============================

                            data = {
                                "name": name,
                                "industry": None,
                                "voivodeship": region,
                                "city": city,
                                "address": address,
                                "phone": phone,
                                "email": email,
                                "website": website,
                                "source": "Google Maps",
                                "scrape_date": str(datetime.date.today())
                            }
                     
                            save_firm(data)

                        except Exception as e:
                            print("Error:", e)
                            continue

        await browser.close()


# ==============================
# RUN WRAPPER
# ==============================

def run_maps():
    asyncio.run(scrape_maps())
