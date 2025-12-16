import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"

def scrape():
    response = requests.get(CATALOG_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    assessments = []

    cards = soup.select("a.product-card")  
    for card in cards:
        title = card.text.strip()
        url = BASE_URL + card["href"]

        detail = requests.get(url)
        dsoup = BeautifulSoup(detail.text, "html.parser")

        desc = dsoup.select_one(".product-description").text.strip()
        test_type = [t.text for t in dsoup.select(".product-tag")]

        assessments.append({
            "name": title,
            "url": url,
            "description": desc,
            "test_type": ",".join(test_type)
        })

        time.sleep(0.5)

    with open("data/shl_catalog.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["name", "url", "description", "test_type"]
        )
        writer.writeheader()
        writer.writerows(assessments)

if __name__ == "__main__":
    scrape()
