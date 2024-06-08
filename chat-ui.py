import streamlit as st
import time
import os
from datetime import datetime
import json
import requests


def response_generator(msg_content):
    lines = msg_content.split('\n')  # Split the content into lines to preserve paragraph breaks.
    for line in lines:
        words = line.split()  # Split the line into words to introduce a delay for each word.
        for word in words:
            yield word + " "
            time.sleep(0.1)
        yield "\n"  # After finishing a line, yield a newline character to preserve paragraph breaks.

def show_msgs():
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            # For assistant messages, use the custom avatar
            with st.chat_message("assistant"):
                st.write(msg["content"])
        else:
            # For user messages, display as usual
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

def chat(message):  
    try:
        url = os.getenv("CHAT_BACKEND_ENDPOINT") + "/chatwithdocument"
        #url = "http://localhost:3000/chatwithdocument"
        params = {
            "question": message,
            "index_name": st.session_state.index_name
        }

        print(params)
        response = requests.get(url, params=params)
        print(response.text)
        return response.text
        #return "This is a test message."
    except Exception as e:
        print(e)
        error_message = str(e).lower()
        return f"An unexpected error occurred: {str(e)}"
        
def main():
    st.title("Chat with your SAP document")
    hasFileUploaded = False
    # Using "with" notation
    with st.sidebar:
        with st.form("my_form"):
            uploaded_file = st.file_uploader("Choose a file to chat with your document")
            if uploaded_file is not None and hasFileUploaded == False:
                # To read file as bytes:
                bytes_data = uploaded_file.getvalue()
                hasFileUploaded = True
            submitted = st.form_submit_button("Index the file", type="primary")
            if submitted:
                    response = requests.post(os.getenv("CHAT_BACKEND_ENDPOINT") + "/indexdocument", data=bytes_data, headers={'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=' + uploaded_file.name})
                    print(response.text)
                    st.session_state['index_name'] = response.text
        
    user_input = st.chat_input("Enter your prompt:", key="1")
    
    if 'show' not in st.session_state:
        st.session_state['show'] = 'True'
    if 'show_chats' not in st.session_state:
        st.session_state['show_chats'] = 'False'
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    show_msgs()

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        messages = "\n".join(msg["content"] for msg in st.session_state.messages)
        # print(messages)
        response = chat(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write_stream(response_generator(response))
    elif st.session_state['messages'] is None:
        st.info("Enter a prompt or load chat above to start the conversation")
   

if __name__ == "__main__":
    main()


