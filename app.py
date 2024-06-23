import streamlit as st
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import datetime

@st.cache_resource
def initialize_llm():
    return Ollama(model="llama2")

# Initialize Ollama LLM
llm = initialize_llm()

# Define the prompt template
prompt = PromptTemplate(
    input_variables=["chat_history"],
    template=(
        "You are an appointment scheduling assistant. Be polite and concise.\n"
        "Chat history:\n{chat_history}\n"
        "Please ask the necessary questions to book an appointment, including the user's name, preferred date and time, and the doctor they want to see.\n"
        "AI:"
    ),
)

# Create the LLMChain
chain = LLMChain(llm=llm, prompt=prompt)

st.title("Doctor Appointment Chatbot")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! Would you like to book an appointment?"}
    ]
if "appointment_info" not in st.session_state:
    st.session_state.appointment_info = {"name": "", "date": "", "time": "", "doctor": ""}
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Function to process user input
def process_input(user_input):
    if user_input:
        # Add user input to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Generate response from LLM
        chat_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])
        response = chain.run(chat_history=chat_history)

        # Add AI response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# Display chat messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    process_input(user_input)
    st.experimental_rerun()
