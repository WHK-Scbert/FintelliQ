import re
import json
from openai import OpenAI
import yfinance as yahooFinance
import requests
from bs4 import BeautifulSoup
import streamlit as st

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


def concatenate_elements(element_list):
    """
    Concatenates all elements in the provided list into a single string.

    Parameters:
    element_list (list): A list of strings to be concatenated

    Returns:
    str: A single string made by concatenating all the elements in the list
    """
    return ''.join(element_list)


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

