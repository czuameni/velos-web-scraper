import re
import requests
from config import HEADERS

def extract_emails(url):

    emails = set()

    try:
        r = requests.get(url, headers=HEADERS, timeout=5)

        matches = re.findall(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            r.text
        )

        emails.update(matches)

    except:
        pass

    return list(emails)