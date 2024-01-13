import requests
from bs4 import BeautifulSoup

content = []

def scrape_http_links(url):
    # Send a request to the URL
    response = requests.get(url)
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find all <a> tags
    all_links = soup.find_all('a')
    # Extract the href attribute from each <a> tag and filter for those starting with 'http'
    filtered_links = [link.get('href') for link in soup.find_all('a')
                      if link.get('href')
                      and link.get('href').startswith('https://www.benzinga.com/news/')
                      and 'tab' not in link.get('class', [])]
    return filtered_links

# Example usage
url = 'https://www.benzinga.com/quote/AAPL/news'
http_links = scrape_http_links(url)
for link in http_links:
    content.append(requests.get(link).text) # Get the content of each link
#print(content[0])
#print(content[5])


counter = 0
for link in http_links:
    if link == "https://www.benzinga.com/news/large-cap/24/01/36618706/bitcoin-debuts-on-wall-street-inflation-spikes-apple-and-tesla-skid-this-week-in-the-markets":
        break
    else:
        counter += 1
print(content[counter])


#https://www.benzinga.com/news/large-cap/24/01/36618706/bitcoin-debuts-on-wall-street-inflation-spikes-apple-and-tesla-skid-this-week-in-the-markets
