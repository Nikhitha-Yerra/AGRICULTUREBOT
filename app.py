import streamlit as st
import requests

st.title("Agriculture Chatbot")

# Replace with your Ngrok URL
RASA_URL = "https://adc8-2405-201-c018-500d-61f3-1006-d0be-d7c6.ngrok-free.app/webhooks/rest/webhook"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    payload = {"sender": "user", "message": user_input}
    response = requests.post(RASA_URL, json=payload)

    bot_reply = ""
    if response.status_code == 200:
        bot_responses = response.json()
        for res in bot_responses:
            bot_reply += res.get("text", "") + "\n"

    if bot_reply:
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
