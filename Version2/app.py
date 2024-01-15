import io
import openai
from openai import OpenAI
import yfinance as yahooFinance
import streamlit as st
import pandas as pd
import os
import time
import tempfile
import requests
import csv
import json
from PIL import Image
import function

def init():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "run" not in st.session_state:
        st.session_state.run = None

    if "file_ids" not in st.session_state:
        st.session_state.file_ids = []
    
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None


        
def assistant_handler(client, assistant_id):
    assistant = client.beta.assistants.retrieve(assistant_id)
    
    assistant_name = assistant.name
    assistant_instructions = assistant.instructions
    model_option = 'gpt-3.5-turbo'
    return assistant, model_option, assistant_instructions
    
        


def news_summary(client, assistant_option, thread_id):
    ticker = st.sidebar.text_input("Enter Stock Ticker:", "AAPL")
    #st.session_state.thread_id = client.beta.threads.create()
    
    if st.sidebar.button("Fetch News"):

        # Create a new thread
        st.session_state.thread_id = client.beta.threads.create().id
        thread_id = st.session_state.thread_id

        # Fetch and display stock information from Yahoo Finance
        CompanyInfo = yahooFinance.Ticker(ticker)
        function.display_company_info(CompanyInfo.info)
        function.display_stock_info(CompanyInfo.info)

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
        st.session_state.messages = st.session_state.messages.append(client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=processed_text,
        ))

        st.session_state.run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_option,
            tools = [{"type": "code_interpreter"}],

        )
        
        print(st.session_state.run)
        pending = False
        while st.session_state.run.status != "completed":
            if not pending:
                with st.chat_message("assistant"):
                    st.markdown("FintelliQ is thinking...")
                pending = True
            time.sleep(3)
            st.session_state.run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=st.session_state.run.id,
            )
            
             
                    
        if st.session_state.run.status == "completed": 
            st.empty()
            chat_display(client)


def chat_prompt(client, assistant_option):
    if prompt := st.chat_input("Enter your message here"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages = st.session_state.messages.append(client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt,
        ))

        st.session_state.run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_option,
            tools = [{"type": "code_interpreter"}],

        )
        
        print(st.session_state.run)
        pending = False
        while st.session_state.run.status != "completed":
            if not pending:
                with st.chat_message("assistant"):
                    st.markdown("FintelliQ is thinking...")
                pending = True
            time.sleep(3)
            st.session_state.run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=st.session_state.run.id,
            )
            
             
                    
        if st.session_state.run.status == "completed": 
            st.empty()
            chat_display(client)

def chat_display(client):
    st.session_state.messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    ).data
    counter = 0
    for message in reversed(st.session_state.messages):
        if message.role in ["user", "assistant"]:
            if counter != 0:
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
            else:
                counter += 1


def main():
    st.title('IntelliQ: The IQ of Investment 📈')
    st.caption('Created by C1C Chanon Mallanoo')
    st.divider()

    client = OpenAI()
    assistant_option = 'asst_vSYVvJ3sGbisAl7wkpANHgwj'

    if st.session_state.thread_id is None:
        st.session_state.thread_id = client.beta.threads.create().id
        print(st.session_state.thread_id)

    news_summary(client, assistant_option, thread_id=st.session_state.thread_id)
    
    st.session_state.current_assistant, st.session_state.model_option, st.session_state.assistant_instructions = assistant_handler(client, assistant_option)
    chat_prompt(client, assistant_option)
            


if __name__ == '__main__':
    init()
    main()




