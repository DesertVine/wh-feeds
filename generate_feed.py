import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET


def get_executive_orders():
    url = "https://www.whitehouse.gov/presidential-actions/executive-orders/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    orders = []
    for article in soup.select("article"):
        title_el = article.select_one("h2 a")
        date_el = article.select_one("time")
        if not title_el or not date_el:
            continue

        link = title_el["href"]
        title = title_el.get_text(strip=True)
        date = date_el["datetime"]

        order_content = fetch_article_preview(link)

        orders.append({
            "title": title,
            "url": link,
            "pubDate": date,
            "content": order_content,
        })

    return orders


def fetch_article_preview(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"[WARN] Couldn't fetch article from {url}")
            return None
        return extract_article_text(response.text, url)
    except Exception as e:
        print(f"[ERROR] Exception fetching article from {url}: {e}")
        return None


def extract_article_text(html, url):
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article")
    if not article:
        print(f"[DEBUG] No <article> found at: {url}")
        return None

    paragraphs = article.find_all("p")
    if len(paragraphs) < 2:
        print(f"[DEBUG] Less than 2 paragraphs found at: {url}")
        return None

    second_para = paragraphs[1].get_text(strip=True)
    return second_para if second_para else None


def build_rss_feed(items):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "White House Executive Orders"
    ET.SubElement(channel, "link").text = "https://www.whitehouse.gov/presidential-actions/executive-orders/"
    ET.SubElement(channel, "description").text = "Latest executive orders from the White House"

    for item in items:
        entry = ET.SubElement(channel, "item")
        ET.SubElement(entry, "title").text = item["title"]
        ET.SubElement(entry, "link").text = item["url"]
        ET.SubElement(entry, "guid").text = item["url"]
        ET.SubElement(entry, "pubDate").text = datetime.fromisoformat(item["pubDate"]).strftime("%a, %d %b %Y %H:%M:%S %z")
        description = item["content"] if item["content"] else "No content found..."
        ET.SubElement(entry, "description").text = description

    return ET.ElementTree(rss)


def main():
    print("RSS feed generation starting...\n")
    print("Fetching Executive Orders...\n")

    eos = get_executive_orders()

    print(f"Found {len(eos)} Executive Orders.\n")
    for eo in eos:
        print(f"- {eo['title']} ({eo['pubDate']})")
        print(f"  → {eo['url']}")
        preview = eo['content'][:120] + "..." if eo['content'] else "No content found..."
        print(f"  ↳ Preview: {preview}\n")

    rss_tree = build_rss_feed(eos)
    rss_tree.write("executive_orders.xml", encoding="utf-8", xml_declaration=True)
    print("✅ RSS feed written to executive_orders.xml")


if __name__ == "__main__":
    main()
