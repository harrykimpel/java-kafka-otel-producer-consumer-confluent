"""Submit a batch of diverse first names to the 'My AI Bot' experiment app
and print the AI response for each one.

Setup (one-time):
    pip install playwright
    playwright install chromium

Run:
    python submit_names.py              # headless
    HEADED=1 python submit_names.py     # watch the browser
"""

import os
import random
import time

from playwright.sync_api import sync_playwright

URL = "https://tzbnhvhtgj.us-east-1.awsapprunner.com/"

SAMPLE_SIZE = 20

NAMES = [
    "Aiko",        # Japanese
    "Mateo",       # Spanish
    "Priya",       # Indian
    "Kwame",       # Akan / Ghanaian
    "Sven",        # Scandinavian
    "Fatima",      # Arabic
    "Liam",        # Irish
    "Mei",         # Chinese
    "Olumide",     # Yoruba
    "Anastasia",   # Russian / Greek
    "Kai",         # Hawaiian
    "Esperanza",   # Spanish
    "Dmitri",      # Russian
    "Amara",       # Igbo
    "Yusuf",       # Arabic / Turkish
    "Ingrid",      # Norse
    "Tariq",       # Arabic
    "Saoirse",     # Irish
    "Nadia",       # Slavic / Arabic
    "Hiroshi",     # Japanese
    "Sakura",      # Japanese
    "Ren",         # Japanese
    "Yuki",        # Japanese
    "Haruki",      # Japanese
    "Akira",       # Japanese
    "Sofia",       # Spanish / Italian
    "Diego",       # Spanish
    "Camila",      # Spanish / Portuguese
    "Santiago",    # Spanish
    "Isabela",     # Portuguese / Spanish
    "Lucia",       # Italian / Spanish
    "Giovanni",    # Italian
    "Chiara",      # Italian
    "Matteo",      # Italian
    "Aurora",      # Italian / Latin
    "Arjun",       # Indian
    "Aanya",       # Indian
    "Rohan",       # Indian
    "Diya",        # Indian
    "Vikram",      # Indian
    "Lakshmi",     # Indian
    "Ravi",        # Indian
    "Ananya",      # Indian
    "Chiamaka",    # Igbo
    "Adaeze",      # Igbo
    "Chibuzo",     # Igbo
    "Adanna",      # Igbo
    "Folake",      # Yoruba
    "Babatunde",   # Yoruba
    "Adebayo",     # Yoruba
    "Ngozi",       # Igbo
    "Kofi",        # Akan
    "Ama",         # Akan
    "Yaa",         # Akan
    "Kojo",        # Akan
    "Zanele",      # Zulu
    "Thabo",       # Sotho / Tswana
    "Lerato",      # Sotho
    "Sipho",       # Zulu
    "Aaliyah",     # Arabic
    "Omar",        # Arabic
    "Layla",       # Arabic
    "Khalid",      # Arabic
    "Zara",        # Arabic / Persian
    "Hassan",      # Arabic
    "Amira",       # Arabic
    "Rashid",      # Arabic
    "Farah",       # Arabic / Persian
    "Jamal",       # Arabic
    "Maryam",      # Arabic / Persian
    "Ibrahim",     # Arabic
    "Soraya",      # Persian
    "Darius",      # Persian
    "Roxana",      # Persian
    "Cyrus",       # Persian
    "Niloofar",    # Persian
    "Kian",        # Persian / Irish
    "Ayşe",        # Turkish
    "Mehmet",      # Turkish
    "Elif",        # Turkish
    "Emre",        # Turkish
    "Wei",         # Chinese
    "Jing",        # Chinese
    "Lei",         # Chinese
    "Xiulan",      # Chinese
    "Chen",        # Chinese
    "Lin",         # Chinese
    "Yan",         # Chinese
    "Min-jun",     # Korean
    "Seo-yeon",    # Korean
    "Ji-ho",       # Korean
    "Ha-eun",      # Korean
    "Joon-woo",    # Korean
    "Linh",        # Vietnamese
    "Anh",         # Vietnamese
    "Minh",        # Vietnamese
    "Thuy",        # Vietnamese
    "Somchai",     # Thai
    "Kanya",       # Thai
    "Niran",       # Thai
    "Achara",      # Thai
    "Sukma",       # Indonesian
    "Budi",        # Indonesian
    "Dewi",        # Indonesian / Balinese
    "Made",        # Balinese
    "Aaliyah",     # Swahili / Arabic
    "Zuri",        # Swahili
    "Jabari",      # Swahili
    "Imani",       # Swahili
    "Niamh",       # Irish
    "Cillian",     # Irish
    "Aoife",       # Irish
    "Sean",        # Irish
    "Eilidh",      # Scottish
    "Hamish",      # Scottish
    "Catriona",    # Scottish
    "Rhys",        # Welsh
    "Bronwen",     # Welsh
    "Gwyneth",     # Welsh
    "Dafydd",      # Welsh
    "Astrid",      # Scandinavian
    "Bjorn",       # Scandinavian
    "Freya",       # Norse
    "Magnus",      # Scandinavian
    "Lars",        # Scandinavian
    "Sigrid",      # Scandinavian
    "Henrik",      # Scandinavian
    "Linnea",      # Swedish
    "Mikkel",      # Danish
    "Saskia",      # Dutch
    "Sander",      # Dutch
    "Ewa",         # Polish
    "Krzysztof",   # Polish
    "Magdalena",   # Polish / Spanish
    "Tomasz",      # Polish
    "Lukas",       # German / Czech
    "Greta",       # German
    "Annika",      # German / Scandinavian
    "Friedrich",   # German
    "Heidi",       # German / Swiss
    "Klaus",       # German
    "Ottilie",     # German
    "Mihai",       # Romanian
    "Ioana",       # Romanian
    "Andrei",      # Romanian / Russian
    "Stefana",     # Romanian
    "Katerina",    # Greek / Slavic
    "Nikos",       # Greek
    "Eleni",       # Greek
    "Yannis",      # Greek
    "Despina",     # Greek
    "Tatiana",     # Russian
    "Sergei",      # Russian
    "Svetlana",    # Russian
    "Mikhail",     # Russian
    "Olga",        # Russian
    "Boris",       # Russian / Bulgarian
    "Yelena",      # Russian
    "Oksana",      # Ukrainian
    "Taras",       # Ukrainian
    "Mykola",      # Ukrainian
    "Aleksandar",  # Serbian
    "Milica",      # Serbian
    "Branislav",   # Serbian / Slovak
    "Jana",        # Czech / Slovak
    "Vaclav",      # Czech
    "Eszter",      # Hungarian
    "Bence",       # Hungarian
    "Zsofia",      # Hungarian
    "Levente",     # Hungarian
    "Naledi",      # Tswana
    "Chenoa",      # Native American
    "Tahoma",      # Native American
    "Ayasha",      # Native American
    "Kalani",      # Hawaiian
    "Leilani",     # Hawaiian
    "Keoni",       # Hawaiian
    "Manaia",      # Maori
    "Aroha",       # Maori
    "Tane",        # Maori
    "Matiu",       # Maori
    "Eitan",       # Hebrew
    "Talia",       # Hebrew
    "Yael",        # Hebrew
    "Avraham",     # Hebrew
    "Shira",       # Hebrew
    "Noa",         # Hebrew
    "Jolanta",     # Lithuanian / Polish
    "Egle",        # Lithuanian
    "Kristaps",    # Latvian
    "Liis",        # Estonian
    "Tarmo",       # Estonian
    "Aino",        # Finnish
    "Eero",        # Finnish
    "Sanna",       # Finnish
    "Mikko",       # Finnish
    "Ekaterina",   # Russian / Bulgarian
    "Bogdan",      # Slavic
    "Radmila",     # Slavic
    "Joaquin",     # Spanish
    "Beatriz",     # Portuguese / Spanish
    "Rafael",      # Portuguese / Spanish
    "Renata",      # Czech / Italian
    "Tiago",       # Portuguese
    "Catarina",    # Portuguese
    "Pedro",       # Portuguese / Spanish
    "Mariana",     # Portuguese / Spanish
    "Joao",        # Portuguese
    "Henrique",    # Portuguese
    "Antoine",     # French
    "Margaux",     # French
    "Camille",     # French
    "Thierry",     # French
    "Solene",      # French
    "Lucien",      # French
    "Adelaide",    # French / German
]


def submit(page, name: str) -> str:
    page.goto(URL, wait_until="domcontentloaded")
    page.fill("#input-textarea", name)
    page.click('button[type="submit"]')
    # The server returns a page with #markdown-preview populated.
    page.wait_for_selector("#markdown-preview", state="attached")
    # Give the LLM-rendered content a moment to settle.
    page.wait_for_function(
        "() => { const el = document.querySelector('#markdown-preview');"
        "        return el && el.innerText.trim().length > 0; }",
        timeout=60_000,
    )
    return page.inner_text("#markdown-preview").strip()


def main() -> None:
    headless = os.environ.get("HEADED") != "1"
    names = random.sample(NAMES, SAMPLE_SIZE)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        for i, name in enumerate(names, 1):
            print(f"\n[{i}/{len(names)}] {name}")
            print("-" * 60)
            try:
                response = submit(page, name)
                print(response)
            except Exception as e:
                print(f"  !! failed: {e}")
            time.sleep(6.0)  # gentle pacing between submissions

        browser.close()


if __name__ == "__main__":
    main()
