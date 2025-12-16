import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}



def scrape_table(table):
    assessments = []
    rows = table.find_all("tr")[1:]  # skip header

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        # Name + URL
        link = cols[0].find("a")
        if not link:
            continue

        name = link.text.strip()
        url = BASE_URL + link["href"]

        # Remote testing
        remote_support = "Yes" if cols[1].find("span", class_="-yes") else "No"

        # Adaptive / IRT
        adaptive_support = "Yes" if cols[2].find("span", class_="-yes") else "No"

        # Test type
        keys = cols[3].find_all("span", class_="product-catalogue__key")
        test_type = ", ".join(k.text.strip() for k in keys) if keys else "N/A"

        assessments.append({
            "name": name,
            "url": url,
            "test_type": test_type,
            "remote_support": remote_support,
            "adaptive_support": adaptive_support,
            "description": "N/A",
            "duration": "N/A"
        })

    return assessments


def enrich_from_detail(assessment):
    try:
        resp = requests.get(assessment["url"], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")

      
        description = ""

        for header in soup.find_all(["h2", "h3", "h4"]):
            if "description" in header.get_text(strip=True).lower():
                p = header.find_next("p")
                if p:
                    description = p.get_text(" ", strip=True)
                    break

        if not description:
            for section in soup.find_all("section"):
                text = section.get_text(" ", strip=True)
                if len(text) > 150 and "assessment" in text.lower():
                    description = text
                    break

        if not description:
            for p in soup.find_all("p"):
                text = p.get_text(" ", strip=True)
                if len(text) > 150:
                    description = text
                    break

        if description:
            assessment["description"] = description

       

        duration = ""

        for p in soup.find_all("p"):
            text = p.get_text(" ", strip=True).lower()

            if "approximate completion time" in text:
                match = re.search(r'(\d+)', text)
                if match:
                    duration = f"{match.group(1)} minutes"
                    break

        if duration:
            assessment["duration"] = duration
            print(f" Found duration: {duration}")


    except Exception as e:
        print(f" Detail fetch failed: {assessment['url']}")

    return assessment



def scrape_shl_catalog():
    all_assessments = []

    print(" Scraping Individual Test Solutions...")

    # type=1 → Individual Test Solutions
    for start in range(0, 400, 12):
        page_url = f"{CATALOG_URL}?start={start}&type=1"
        print("Fetching:", page_url)

        resp = requests.get(page_url, headers=HEADERS)
        if resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table")
        if not table:
            break

        rows = scrape_table(table)
        if not rows:
            break

        all_assessments.extend(rows)
        time.sleep(1)

    print(f"Found {len(all_assessments)} assessments in catalog")

    # Enrich with detail pages
    for i, assessment in enumerate(all_assessments, 1):
        print(f"Enriching {i}/{len(all_assessments)}")
        enrich_from_detail(assessment)
        time.sleep(0.5)

    return pd.DataFrame(all_assessments)



if __name__ == "__main__":
    print(" Starting SHL catalog scraping...")
    df = scrape_shl_catalog()

    if len(df) < 377:
        print("ERROR: Less than 377 Individual Test Solutions found!")
    else:
        print("equirement satisfied")

    df.to_csv("data/shl_catalog.csv", index=False)
    print("Saved to data/shl_catalog.csv")
