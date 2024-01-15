import re
import json
from openai import OpenAI
import yfinance as yahooFinance
import requests
from bs4 import BeautifulSoup
import streamlit as st
import time

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

def clean_text(text):
    # Remove HTML tags
    clean = re.sub(r'<.*?>', '', text)
    
    # Remove any remaining HTML/CSS elements and attributes
    clean = re.sub(r'{.*?}', '', clean)
    clean = re.sub(r'\[.*?\]', '', clean)
    
    # Replace multiple spaces, newlines, or tabs with a single space
    clean = re.sub(r'\s+', ' ', clean)

    return clean.strip()

def extract_content(text):
    # Send a request to the URL

    # Check if the request was successful
    
    # Parse the content of the webpage
    soup = BeautifulSoup(text, 'html.parser')

    for script in soup.find_all('script'):
        script.decompose()
    for script in soup.find_all('span'):
        script.decompose()

    paragraphs = soup.find_all('p')

    readable_text = '\n'.join([p.get_text() for p in paragraphs])

    return readable_text


def display_assistant_message(message):
    stored_messages = []
    st.session_state.messages = message

    for message in reversed(st.session_state.messages):
        if message.role in ["assistant"]:
            for content in message.content:
                if content.type == "text":
                    stored_messages.append(content.text.value)
                else:
                    stored_messages.append(content)
    
    with st.chat_message("assistant"):
        st.markdown(stored_messages[-1])
        print(len(stored_messages))



    # for message in reversed(st.session_state.messages):
    #         if message.role in ["assistant"]:
    #             with st.chat_message(message.role):
    #                 for content in message.content:
    #                     if content.type == "text":
    #                         st.markdown(content.text.value)
    #                     elif content.type == "image_file":
    #                         image_file = content.image_file.file_id
    #                         image_data = client.files.content(image_file)
    #                         image_data = image_data.read()
    #                         #save image to temp file
    #                         temp_file = tempfile.NamedTemporaryFile(delete=False)
    #                         temp_file.write(image_data)
    #                         temp_file.close()
    #                         #display image
    #                         image = Image.open(temp_file.name)
    #                         st.image(image)
    #                     else:
    #                         st.markdown(content)

# Chatgpt handler
def gpt_handler(assistance_ID, processed_text, thread, client, type="news"):
    
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=processed_text
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistance_ID,
        instructions="Sanitize all the unreadable data and put it into bullet points"
    )

    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    
    st.session_state.run = run
    pending = False
    while st.session_state.run.status != "completed":
        if not pending:
            if type != "first":
                with st.chat_message("assistant"):
                    st.markdown("Processing...")
            pending = True
        time.sleep(3)
        st.session_state.run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        
            
    if st.session_state.run.status == "completed": 
        st.empty()
    
    st.session_state.messages = client.beta.threads.messages.list(
            thread_id=thread.id
        ).data
    return st.session_state.messages









# Function to display company information
def display_company_info(info):
    st.subheader("Company Information")
    st.write(f"**Address:** {info['address1']}, {info['city']}, {info['zip']}, {info['country']}")
    st.write(f"**Phone:** {info['phone']}")
    st.write(f"**Website:** [Link]({info['website']})")
    st.write(f"**Industry:** {info['industryDisp']}")
    st.write(f"**Sector:** {info['sectorDisp']}")
    st.write("### Business Summary")
    st.write(info['longBusinessSummary'])

# Function to display stock information
def display_stock_info(info):
    st.subheader("Stock Information")
    st.write(f"**Previous Close:** {info['previousClose']}")
    st.write(f"**Open:** {info['open']}")
    st.write(f"**Day Low:** {info['dayLow']}")
    st.write(f"**Day High:** {info['dayHigh']}")
    st.write(f"**Volume:** {info['volume']}")
    # Add more fields as needed

# # Your stock data
# stock_data = {
#     "address1": "Building 20",
#     "address2": "No. 56 AnTuo Road Anting Town Jiading District",
#     "city": "Shanghai",
#     "zip": "201804",
#     "country": "China",
#     "phone": "86 21 6908 2018",
#     "website": "https://www.nio.com",
#     "industry": "Auto Manufacturers",
#     "industryDisp": "Auto Manufacturers",
#     "sector": "Consumer Cyclical",
#     "sectorDisp": "Consumer Cyclical",
#     "longBusinessSummary": "NIO Inc. designs, develops, manufactures, and sells smart electric vehicles in China...",
#     # ... add the rest of your data here
#     "previousClose": 7.4,
#     "open": 7.26,
#     "dayLow": 7.16,
#     "dayHigh": 7.53,
#     "volume": 49034582
#     # ... and so on
# }
