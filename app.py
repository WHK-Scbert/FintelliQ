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

    assistance_ID = 'asst_vSYVvJ3sGbisAl7wkpANHgwj'
    


    


    if st.sidebar.button("Fetch News"):
        url = f'https://www.benzinga.com/quote/{ticker}/news'
        http_links = function.scrape_http_links(url)
        content = [requests.get(link).text for link in http_links]
        concatenated_news = function.concatenate_elements(content)
        #concatenated_news = concatenated_news[:32000]
        processed_text = function.extract_content(concatenated_news)

        # processed_text = function.process_text_with_regex(concatenated_news)
        # processed_text = function.clean_text(processed_text)
        # processed_text = processed_text[:32000]
        print(processed_text)

        thread = client.beta.threads.create()
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
        
        for message in reversed(st.session_state.messages):
            if message.role in ["assistant"]:
                with st.chat_message(message.role):
                    for content in message.content:
                        if content.type == "text":
                            st.markdown(content.text.value)
                        elif content.type == "image_file":
                            image_file = content.image_file.file_id
                            image_data = client.files.content(image_file)
                            image_data = image_data.read()
                            #save image to temp file
                            temp_file = tempfile.NamedTemporaryFile(delete=False)
                            temp_file.write(image_data)
                            temp_file.close()
                            #display image
                            image = Image.open(temp_file.name)
                            st.image(image)
                        else:
                            st.markdown(content)

        # Fetch and display stock information
        st.subheader("Stock Information")
        GetStockInformation = yahooFinance.Ticker(ticker)
        data = ""
        for key, value in GetStockInformation.info.items():
            data += f"{key}: {value}\n"
        st.text_area("Stock Data", data, height=500)

        # Use OpenAI to analyze text (You need to handle the API call here)
        # ...
        # Show the result


# Run the application
if __name__ == "__main__":
    init()
    main()
