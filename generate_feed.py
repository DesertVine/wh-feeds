import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
import re

BASE_URL = "https://www.whitehouse.gov"
EO_URL = f"{BASE_URL}/presidential-actions/executive-orders/"

def extract_article_text(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        article = soup.find("article")
        if article:
            paragraphs = article.find_all("p")

            # Regex pattern to find "Section x. Purpose" or "Sec. x. Purpose", case-insensitive
            pattern = re.compile(r'^(sec(?:tion)?\s+\d+\.?\s+purpose[:.]?)', re.IGNORECASE)

            for p in paragraphs:
                text = p.get_text(strip=True)
                if pattern.match(text):
                    return text

            # Fallback to first non-boilerplate paragraph
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and not text.lower().startswith("by the authority vested in me"):
                    return text

        # Fallback to meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"]

        return None

    except Exception as e:
        print(f"❌ Error extracting article text from {url}: {e}")
        return None

def get_executive_orders():
    print("Fetching Executive Orders...")
    response = requests.get(EO_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    orders = []

    posts = soup.select("li.wp-block-post")

    for post in posts[:10]:  # limit to most recent 10
        title_tag = post.select_one("h2.wp-block-post-title a")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        url = title_tag['href']
        full_url = url if url.startswith("http") else BASE_URL + url

        date_tag = post.select_one("time")
        date = date_tag['datetime'] if date_tag and date_tag.has_attr("datetime") else None

        content = extract_article_text(full_url)

        orders.append({
            'title': title,
            'url': full_url,
            'date': date,
            'content': content
        })

    return orders

def build_rss_feed(items):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Recent Executive Orders"
    ET.SubElement(channel, "link").text = EO_URL
    ET.SubElement(channel, "description").text = "Latest Executive Orders from the White House"

    for item in items:
        entry = ET.SubElement(channel, "item")
        ET.SubElement(entry, "title").text = item["title"]
        ET.SubElement(entry, "link").text = item["url"]
        ET.SubElement(entry, "guid").text = item["url"]

        if item["date"]:
            pub_date = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
            ET.SubElement(entry, "pubDate").text = pub_date.strftime("%a, %d %b %Y %H:%M:%S %z")

        ET.SubElement(entry, "description").text = item["content"] or "No content found."

    return ET.tostring(rss, encoding="unicode")

def main():
    print("RSS feed generation starting...\n")

    eos = get_executive_orders()

    print(f"\nFound {len(eos)} Executive Orders.\n")
    for eo in eos:
        print(f"- {eo['title']} ({eo['date']})")
        print(f"  → {eo['url']}")
        preview = eo['content'][:120] + "..." if eo['content'] else "No content found..."
        print(f"  ↳ Preview: {preview}\n")

    feed = build_rss_feed(eos)

    with open("executive_orders.xml", "w", encoding="utf-8") as f:
        f.write(feed)
    print("✅ RSS feed written to executive_orders.xml")

if __name__ == "__main__":
    main()
