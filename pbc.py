from db import setup_db
from maps_scraper import run_maps
from exporter import export_csv


def main():

    print("Setting up database...")
    setup_db()

    print("Scraping Google Maps...")
    run_maps()

    print("Exporting CSV...")
    export_csv()

    print("Done.")


if __name__ == "__main__":
    main()
