import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.whitehouse.gov"
EO_URL = f"{BASE_URL}/presidential-actions/executive-orders/"

def get_executive_orders():
    print("Fetching Executive Orders...")
    response = requests.get(EO_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    orders = []

    # Look for the new WordPress-based post listings
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

def extract_article_text(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')

        article = soup.select_one("div.body-content") or soup.select_one("article")
        if not article:
            return "No content found."

        paragraphs = [p.text.strip() for p in article.select("p") if p.text.strip()]
        return "\n\n".join(paragraphs[:6])  # Get the first few meaningful paragraphs
    except Exception as e:
        return f"Error fetching content: {e}"

def main():
    print("RSS feed generation starting...\n")
    eos = get_executive_orders()

    print(f"Found {len(eos)} Executive Orders.\n")
    for eo in eos:
        print(f"- {eo['title']} ({eo['date']})")
        print(f"  → {eo['url']}")
        print(f"  ↳ Preview: {eo['content'][:120]}...\n")

if __name__ == "__main__":
    main()
