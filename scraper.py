import requests
from bs4 import BeautifulSoup
import json
import os

# URLs
parent_url = 'https://marantec-group.softgarden.io/de/widgets/internaljobs'
content_url = 'https://marantec-group.softgarden.io/de/job-offers/internal?1&view-mode=widget'

# More comprehensive headers to mimic a real browser request from within an iframe
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': parent_url,
    'Sec-Ch-Ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'iframe',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}

# Use a session object to handle cookies automatically
session = requests.Session()

print("Step 1: Visiting parent page to get session cookies...")
try:
    # First, visit the parent page to establish a session.
    session.get(parent_url, headers={'User-Agent': headers['User-Agent']})
    print("Successfully established a session.")

    print("Step 2: Fetching the actual job listing content...")
    # Now, fetch the actual content, the session will automatically send the cookies.
    response = session.get(content_url, headers=headers)
    response.raise_for_status()  # This will raise an error if the status is not 200
    print("Successfully fetched job data.")

    # --- Start Parsing ---
    soup = BeautifulSoup(response.text, 'html.parser')
    job_articles = soup.find_all('article', class_='job-posting')
    
    jobs_list = []

    print(f"Found {len(job_articles)} job articles.")

    for article in job_articles:
        link_node = article.find('a')
        href = link_node['href'] if link_node else '#'

        # Make URL absolute
        if not href.startswith('http'):
            href = 'https://marantec-group.softgarden.io' + href

        title_node = article.find(class_='job-posting-title')
        title = title_node.get_text(strip=True) if title_node else 'Unbekannter Titel'

        meta_nodes = article.find(class_='job-posting-meta').find_all('span')
        details = [meta.get_text(strip=True) for meta in meta_nodes]

        jobs_list.append({
            'title': title,
            'link': href,
            'description': ' | '.join(details),
            'guid': href,
            'pubDate': '' # pubDate will be set by the PHP script on fetch
        })

    # --- End Parsing ---

    # Write the data to jobs.json
    output_file = 'jobs.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(jobs_list, f, ensure_ascii=False, indent=4)

    print(f"Successfully wrote {len(jobs_list)} jobs to {output_file}.")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
    exit(1)

