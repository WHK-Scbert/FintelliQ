import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from openai import OpenAI
import yfinance as yahooFinance
import function
import time


def init():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "run" not in st.session_state:
        st.session_state.run = None

    if "file_ids" not in st.session_state:
        st.session_state.file_ids = []
    
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None


# Streamlit application starts here
def main():
    st.title("FintelliQ: The IQ of Investment")

    # Sidebar for user input
    ticker = st.sidebar.text_input("Enter Stock Ticker:", "NIO")
    client = OpenAI()
    msft = yahooFinance.Ticker(ticker)

    assistance_ID = 'asst_vSYVvJ3sGbisAl7wkpANHgwj'

    
    if st.sidebar.button("Fetch News"):
        thread = client.beta.threads.create()

        # Clear the previous messages
        st.empty()

        # Fetch news from Yahoo Finance
        #yahoo_news = ""
        #yahoo_links = msft.news
        #for source in yahoo_links:
            #print(source['link'])
        #    content = requests.get(source['link']).text
        #    yahoo_news += function.extract_content(content)
        
        #st.session_state.general_news = function.gpt_handler(assistance_ID, yahoo_news, thread, client, "first")

        # Fetch news from Benzinga
        url = f'https://www.benzinga.com/quote/{ticker}/news'
        http_links = function.scrape_http_links(url)
        content = [requests.get(link).text for link in http_links]
        concatenated_news = function.concatenate_elements(content)
        processed_text = function.extract_content(concatenated_news)
        if len(processed_text) > 32767:
            processed_text = processed_text[:32767]

        # Analyze the news with IntelliQ Assistance
        st.session_state.messages = function.gpt_handler(assistance_ID, processed_text, thread, client)
        
        # Display the assistant messages
        function.display_assistant_message(st.session_state.messages)
    

        # Fetch and display stock information from Yahoo Finance
        CompanyInfo = yahooFinance.Ticker(ticker)
        function.display_company_info(CompanyInfo.info)
        function.display_stock_info(CompanyInfo.info)

        # Delete message and thread
        client.beta.threads.delete(thread.id)



# Run the application
if __name__ == "__main__":
    init()
    main()
