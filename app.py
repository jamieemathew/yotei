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
    input_variables=["chat_history", "human_input"],
    template="You are an appointment scheduling assistant. Be polite and concise. Chat history: {chat_history}\nHuman: {human_input}\nAI:",
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
if "current_question" not in st.session_state:
    st.session_state.current_question = "start"
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Function to process user input
def process_input(user_input):
    if user_input:
        # Add user input to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Process user input based on current question
        if st.session_state.current_question == "start":
            if "yes" in user_input.lower():
                st.session_state.current_question = "name"
                response = "Great! Let's start booking your appointment. What's your name?"
            else:
                response = "Alright. Is there anything else I can help you with?"
        elif st.session_state.current_question == "name":
            st.session_state.appointment_info["name"] = user_input
            st.session_state.current_question = "date"
            response = "Nice to meet you, {}! What date would you like to schedule the appointment? (Please use YYYY-MM-DD format)".format(user_input)
        elif st.session_state.current_question == "date":
            try:
                date = datetime.datetime.strptime(user_input, "%Y-%m-%d").date()
                st.session_state.appointment_info["date"] = user_input
                st.session_state.current_question = "time"
                response = "Got it. What time would you prefer? (Please use HH:MM format)"
            except ValueError:
                response = "I'm sorry, that's not a valid date format. Please use YYYY-MM-DD."
        elif st.session_state.current_question == "time":
            try:
                time = datetime.datetime.strptime(user_input, "%H:%M").time()
                st.session_state.appointment_info["time"] = user_input
                st.session_state.current_question = "doctor"
                response = "Noted. Which doctor would you like to see?"
            except ValueError:
                response = "I'm sorry, that's not a valid time format. Please use HH:MM."
        elif st.session_state.current_question == "doctor":
            st.session_state.appointment_info["doctor"] = user_input
            st.session_state.current_question = "confirm"
            response = f"Great! Here's a summary of your appointment:\nName: {st.session_state.appointment_info['name']}\nDate: {st.session_state.appointment_info['date']}\nTime: {st.session_state.appointment_info['time']}\nDoctor: {st.session_state.appointment_info['doctor']}\nIs this correct? (Yes/No)"
        elif st.session_state.current_question == "confirm":
            if user_input.lower() == "yes":
                response = "Your appointment has been scheduled. Thank you!"
                st.session_state.current_question = "done"
            else:
                st.session_state.current_question = "name"
                st.session_state.appointment_info = {"name": "", "date": "", "time": "", "doctor": ""}
                response = "I'm sorry for the confusion. Let's start over. What's your name?"
        else:
            # Use LangChain for general conversation
            response = chain.run(chat_history="\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history]), human_input=user_input)

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