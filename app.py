import streamlit as st
import requests

st.title("Agriculture Chatbot")

# Your deployed Rasa server URL on Render
RASA_URL = "https://agriculture-chatbot-fzlv.onrender.com/webhooks/rest/webhook"

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
    try:
        response = requests.post(RASA_URL, json=payload, timeout=10)
        bot_reply = ""

        if response.status_code == 200:
            bot_responses = response.json()
            for res in bot_responses:
                bot_reply += res.get("text", "") + "\n"
        else:
            bot_reply = "Error: Couldn't connect to the chatbot server."

    except requests.exceptions.RequestException:
        bot_reply = "Error: Connection timed out. Please try again later."

    if bot_reply:
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
