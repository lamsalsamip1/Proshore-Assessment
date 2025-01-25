import os
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage
from validate import validate_date, validate_email
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
import streamlit as st
import psycopg2


db_host = 'cleancam.postgres.database.azure.com'
db_name = 'postgres'
db_user = 'lamsalsamip'
db_pass = os.getenv('AZURE_DB_PASSWORD')

conn = psycopg2.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_pass
    )
cur = conn.cursor()


llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",  # or your deployment
    api_version="2024-08-01-preview",# or your api version
)

AZURE_OPENAI_ENDPOINT='https://samip-m42jr2pq-eastus2.cognitiveservices.azure.com/openai/deployments/text-embedding-3-small-2/embeddings?api-version=2023-05-15'

embedding_function= AzureOpenAIEmbeddings(model="text-embedding-3-small"
                                  ,api_key=os.getenv("AZURE_OPENAI_EMBEDDING_KEY"),
                                  azure_endpoint=AZURE_OPENAI_ENDPOINT,
                                  openai_api_version="2023-05-15")

# Load the existing Chroma vectorstore
vectordb = Chroma(
    persist_directory="chroma/",
    embedding_function=embedding_function
)
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

# History-aware retriever setup
contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# Create the retrieval chain
qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \

{context}"""
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# Booking tool definition
@tool
def booking_tool(destination:str,date:str,name:str) -> str:
    """
    This tool books a trekking package when user wants to make any kind of booking. It expects three inputs: destination,date, and name. If successfull, it returns 'Booking successful'. If the booking fails, it returns 'Booking failed'.
    """
    date=validate_date(date)
    # Save booking details to a database
    cur.execute(f"INSERT INTO bookings (name,date,destination) VALUES ('{name}', '{date}', '{destination}');")
    conn.commit()
    return "Booking successful"

@tool
def rag_chain_tool(query: str, chat_history: list) -> str:
    """ Tool to invoke the RAG chain with the given query and chat history. """
    return rag_chain.invoke({"input": query, "chat_history": chat_history})["answer"]
# Define tools
tools = [
    booking_tool,
    rag_chain_tool
]

#Define agent prompt
agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", (
            "You are a smart assistant capable of answering questions related to trekking and managing bookings."
            "You have two tools at your disposal:\n"
            "- Use the `rag_chain_tool` for providing information or answering questions related to trekking. Avoid providing standalone answers without the tool. While invoking this tool, pass the query and chat history exactly as it is, with no changes.\n"
            "- Use the `booking_tool` for handling bookings and reservations. When the user wants to make a booking, sequentially ask for destination, date, and name. Once you have this information, call the booking tool by passing these 3 parameters.\n"
            "Always invoke the `rag_chain_tool` if user asks any sort of a question.\n"
            "The only exception is when the user's input is a simple greeting (e.g., 'hi', 'hello', 'hey'), in which case you can respond directly without using a tool. "
        )),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

# Create agent
agent = create_tool_calling_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools,verbose=True)

# Chat interface
# MAX_CHAT_HISTORY_LENGTH=5
# chat_history = []
# while True:
#     user_input = input("You: ")
#     response = agent_executor.invoke({"input": user_input, "chat_history": chat_history})

#     print("Bot:", response['output'])

#     # Update chat history only if the booking tool wasn't invoked
#     if "booking_tool" not in response.get('tool_used', ''):  # Check if 'booking_tool' is invoked
#         chat_history.append(HumanMessage(content=user_input))
#         chat_history.append(AIMessage(content=response['output']))
#     else :
#         chat_history.clear()  
    
#     # Keep chat history length in check
#     if len(chat_history) > MAX_CHAT_HISTORY_LENGTH:
#         chat_history = chat_history[-MAX_CHAT_HISTORY_LENGTH:]

   
# Chat function
def chatbot(user_input, chat_history):
    response = agent_executor.invoke({"input": user_input, "chat_history": chat_history})
    return response
   
