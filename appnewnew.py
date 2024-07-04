import streamlit as st
import sqlite3
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from streamlit_chat import message

# Initialize the Ollama model from langchain
@st.cache_resource
def initialize_llm():
    return Ollama(model="llama2")

# Initialize Ollama LLM
llm = initialize_llm()

# Define the prompt template for the chatbot
prompt = PromptTemplate(
    input_variables=["chat_history"],
    template=(
        "You are an appointment scheduling assistant. Be polite and concise.\n"
        "Chat history:\n{chat_history}\n"
        "Please ask the necessary questions to book an appointment, including the user's name, preferred date and time, and the doctor they want to see.\n"
        "AI:"
    ),
)

# Create the LLMChain for the chatbot
chain = LLMChain(llm=llm, prompt=prompt)

# Function to create a connection to SQLite database
def create_connection():
    conn = sqlite3.connect('appointments.db')
    return conn

# Function to fetch appointments for a clinic from the database
def fetch_appointments(clinic_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM appointments WHERE clinic_id = ?', (clinic_id,))
    appointments = cursor.fetchall()
    conn.close()
    return appointments

# Function to authenticate clinic based on clinic ID and password
def authenticate_clinic(clinic_id, password):
    # Hardcoded clinic login details
    hardcoded_clinic_id = "clinic123"
    hardcoded_password = "password123"
    return clinic_id == hardcoded_clinic_id and password == hardcoded_password

# Streamlit application main function
def main():
    st.title("Yotei")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Chatbot", "Login and View Appointments"])

    # Display selected page
    if selection == "Chatbot":
        chatbot_page()
    elif selection == "Login and View Appointments":
        login_page()

# Chatbot page
def chatbot_page():
    st.title("Doctor Appointment Chatbot")

    # Initialize or retrieve chat history from session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! Would you like to book an appointment?"}
        ]

    # Display chat messages
    for i, message_data in enumerate(st.session_state.chat_history):
        if message_data["role"] == "assistant":
            message(message_data["content"], is_user=False, key=f"assistant_{i}")
        elif message_data["role"] == "user":
            message(message_data["content"], is_user=True, key=f"user_{i}")

    # Chat input
    user_input = st.text_input("Type your message here...")

    if st.button("Send"):
        if user_input:
            # Add user input to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Generate response from LLM
            chat_history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])
            response = chain.run(chat_history=chat_history_text)

            # Add AI response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.experimental_rerun()

# Login and database view page
def login_page():
    st.title("Clinic Login")

    # Clinic login form
    clinic_id = st.text_input("Clinic ID")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Authentication logic
        if authenticate_clinic(clinic_id, password):
            st.success("Logged in successfully!")
            display_appointments(clinic_id)
        else:
            st.error("Invalid credentials. Please try again.")

# Function to display appointments for a logged-in clinic
def display_appointments(clinic_id):
    st.title("Clinic Appointments")

    # Fetch appointments
    appointments = fetch_appointments(clinic_id)

    if appointments:
        st.write("Your Appointments:")
        for appointment in appointments:
            st.write(f"Name: {appointment[2]}, Date: {appointment[3]}, Time: {appointment[4]}, Doctor: {appointment[5]}")
    else:
        st.write("No appointments found.")

if __name__ == "__main__":
    main()
