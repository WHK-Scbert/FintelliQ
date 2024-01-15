import re
import json
from openai import OpenAI
import yfinance as yahooFinance
import requests
from bs4 import BeautifulSoup

ticker = "NIO"


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
url = f'https://www.benzinga.com/quote/{ticker}/news'
http_links = scrape_http_links(url)
for link in http_links:
    content.append(requests.get(link).text) # Get the content of each link

'''
counter = 0
for link in http_links:
    if link == "https://www.benzinga.com/news/large-cap/24/01/36618706/bitcoin-debuts-on-wall-street-inflation-spikes-apple-and-tesla-skid-this-week-in-the-markets":
        break
    else:
        counter += 1
#print(content[counter])

news = content[counter]
'''
def concatenate_elements(element_list):
    """
    Concatenates all elements in the provided list into a single string.

    Parameters:
    element_list (list): A list of strings to be concatenated

    Returns:
    str: A single string made by concatenating all the elements in the list
    """
    return ''.join(element_list)

# Example usage of the function

concatenated_news = concatenate_elements(content)
#print(concatenated_news)

def process_text_with_regex(text):
    """
    Process the given text to:
    1. Remove text within angle brackets < >
    2. Remove words containing '@' or '.'

    Parameters:
    text (str): The input text to be processed

    Returns:
    str: Processed text
    """
    # Remove content within angle brackets
    cleaned_text = re.sub(r'<.*?>', '', text)
    cleaned_text = re.sub(r'{.*?}', '', cleaned_text)
    cleaned_text = re.sub(r'[.*?]', '', cleaned_text)

    # Remove words containing '@', '.', '/', '!', '#'
    cleaned_text = ' '.join(word for word in cleaned_text.split() if not any(char in word for char in '@./\!#%;') or word.startswith('-'))

    return cleaned_text

# Example usage

processed_text = process_text_with_regex(concatenated_news)



processed_text = processed_text[:150000]



#print(processed_text)


client = OpenAI()

print("Stock Information:")
completion = client.chat.completions.create(
    model="gpt-4-1106-preview",  # Updated to use GPT-4
    messages=[
        {"role": "system", "content": f"Analyze {processed_text} and make it into bullet points."}
    ]
)

# Extract the message from the completion
response = str(completion.choices[0].message)

matches = re.findall(r'"(.*?)"', response)
print(matches)


#print(response)

'''
ticker = "AAPL"

GetStockInformation = yahooFinance.Ticker(ticker)
data = ""
# get all key value pairs that are available
for key, value in GetStockInformation.info.items():
	s2 = f"{key}, :, {value}\n"
	data += s2
#print(data)
'''