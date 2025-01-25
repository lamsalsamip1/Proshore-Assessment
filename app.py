from chatnew import chatbot
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage



st.title("AI Trekking Agent")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    role = "user" if isinstance(message, HumanMessage) else "assistant"  # Determine role from message type
    with st.chat_message(role):
        st.markdown(message.content) 

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    # st.session_state.messages.append({"role": "user", "content": prompt})

    # response = f"Echo: {prompt}"
    response = chatbot(prompt, st.session_state.messages)

    st.session_state.messages.append(HumanMessage(content=prompt))
    st.session_state.messages.append(AIMessage(content=response['output']))
    # print(chat_history)
    # Keep chat history length in check
    

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response['output'])
    # Add assistant response to chat history
    