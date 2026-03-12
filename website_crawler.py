import re
import requests
import base64

from playwright.sync_api import sync_playwright
from config import HEADERS


# ==============================
# REGEX
# ==============================

EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"


# ==============================
# CLEAN
# ==============================

def clean_emails(emails):

    clean = []

    for mail in emails:

        if any(x in mail.lower() for x in [
            "example",
            "test",
            "noreply",
            "no-reply"
        ]):
            continue

        clean.append(mail)

    return list(set(clean))


# ==============================
# OBFUSCATION DECODE
# ==============================

def decode_obfuscation(text):

    text = text.replace(" [at] ", "@")
    text = text.replace("(at)", "@")
    text = text.replace(" at ", "@")

    text = text.replace(" [dot] ", ".")
    text = text.replace("(dot)", ".")
    text = text.replace(" dot ", ".")

    return text


# ==============================
# CLOUDFLARE DECODE
# ==============================

def decode_cfemail(cfemail):

    r = int(cfemail[:2], 16)
    email = ''.join(
        chr(int(cfemail[i:i+2], 16) ^ r)
        for i in range(2, len(cfemail), 2)
    )

    return email


# ==============================
# REQUEST SCAN
# ==============================

def scan_requests(url):

    emails = []

    try:
        r = requests.get(url, headers=HEADERS, timeout=6)

        html = decode_obfuscation(r.text)

        emails.extend(re.findall(EMAIL_REGEX, html))

        # cfemail
        cfemails = re.findall(r'data-cfemail="(.*?)"', html)

        for enc in cfemails:
            emails.append(decode_cfemail(enc))

    except:
        pass

    return emails


# ==============================
# PLAYWRIGHT JS SCAN
# ==============================

def scan_js(url):

    emails = []

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=10000)
            page.wait_for_timeout(5000)

            html = page.content()

            emails.extend(re.findall(EMAIL_REGEX, html))

            browser.close()

    except:
        pass

    return emails


# ==============================
# MAIN CRAWLER
# ==============================

def crawl_website(base_url):

    emails_found = []

    paths = [
        "",
        "/kontakt",
        "/contact",
        "/o-nas",
        "/about",
        "/impressum",
        "/privacy",
        "/polityka-prywatnosci"
    ]

    for path in paths:

        url = base_url.rstrip("/") + path

        emails_found.extend(scan_requests(url))
        emails_found.extend(scan_js(url))

    return clean_emails(emails_found)
