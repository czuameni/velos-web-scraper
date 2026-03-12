# Velos – Google Maps Web Scraper

Velos is a Python-based desktop tool for automatically building business databases by scraping Google Maps.

The application collects company information such as:

- company name
- address
- phone number
- website
- email (if found on the website)

The data is stored in a local SQLite database and can be exported to CSV or browsed through a desktop GUI.

---

# Features

• Automated Google Maps scraping  
• Multi-region and multi-city support  
• Multi-keyword search system  
• Email crawler from company websites  
• SQLite database storage  
• CSV export  
• Desktop GUI for browsing the database  
• Search and filtering tools  
• Email copy shortcut for outreach

---

# Technologies Used

- Python
- Playwright
- SQLite
- Pandas
- Tkinter

---

# Installation

Clone the repository:

git clone https://github.com/czuameni/velos-web-scraper.git

cd velos-web-scraper

Install dependencies:

pip install -r requirements.txt

Install Playwright browsers:

playwright install

---

# Running the Scraper

python pbc.py

---

# Running GUI

python gui_app.py

---

# Author

Created by czuameni