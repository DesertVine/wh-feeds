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

    # Updated selector based on the new HTML structure
    for article in soup.select("div.search-results > article")[:10]:
        title_tag = article.select_one("h2 a")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link = title_tag['href']
        date_tag = article.select_one("time")
        date = date_tag['datetime'] if date_tag and date_tag.has_attr("datetime") else None

        full_url = link if link.startswith("http") else BASE_URL + link
        content = extract_article_text(full_url)

        orders.append({
            'title': title,
            'url': full_url,
            'date': date,
            'content': content
        })

    return orders
