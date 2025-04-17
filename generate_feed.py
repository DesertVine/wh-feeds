import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

BASE_URL = "https://www.whitehouse.gov"
EO_URL = f"{BASE_URL}/presidential-actions/executive-orders/"

def get_executive_orders():
    print("Fetching Executive Orders...")
    response = requests.get(EO_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    orders = []

    for article in soup.select("li.podcast-item")[:10]:  # limit to latest 10 for now
        title_tag = article.select_one("h2 a")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link = title_tag['href']
        date_tag = article.select_one("time")
        date = date_tag['datetime'] if date_tag else None

        full_url = link if link.startswith("http") else BASE_URL + link
        content = extract_article_text(full_url)

        orders.append({
            'title': title,
            'url': full_url,
            'date': date,
            'content': content
        })

    return orders

def extract_article_text(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        article = soup.select_one("div.body-content") or soup.select_one("article")

        if article:
            paragraphs = [p.text.strip() for p in article.select("p") if p.text.strip()]
            
            # Filter out boilerplate and preamble-like sections
            good_paragraphs = []
            for p in paragraphs:
                if len(p) < 50:  # too short, likely junk
                    continue
                if p.lower().startswith(("by the authority", "section", "now, therefore", "this order")):
                    continue
                good_paragraphs.append(p)

            return "\n\n".join(good_paragraphs[:8])  # limit to ~8 decent paragraphs

    except Exception as e:
        print(f"Error extracting {url}: {e}")
    return ""

def main():
    print("RSS feed generation starting...")
    eos = get_executive_orders()

    print(f"Found {len(eos)} Executive Orders.")
    for eo in eos:
        print(f"- {eo['title']} ({eo['date']})")

if __name__ == "__main__":
    main()
