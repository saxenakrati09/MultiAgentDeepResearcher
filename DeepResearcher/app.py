import streamlit as st  # Import the Streamlit library for building web apps
from agents import run_research  # Import the run_research function from the agents module
import os  # Import the os module for environment variable management

# Set up page configuration
st.set_page_config(page_title="🔍 Agentic Deep Researcher Using DeepSeek and ollama", layout="wide")  # Set the Streamlit page title and layout

# Initialize session state variables
if "linkup_api_key" not in st.session_state:  # Check if the API key is stored in session state
    st.session_state.linkup_api_key = ""  # If not, initialize it as an empty string
if "messages" not in st.session_state:  # Check if the chat messages are stored in session state
    st.session_state.messages = []  # If not, initialize as an empty list

def reset_chat():
    st.session_state.messages = []  # Function to clear the chat history

# Sidebar: Linkup Configuration with updated logo link
with st.sidebar:  # Create a sidebar section
    col1, col2 = st.columns([1, 3])  # Create two columns in the sidebar
    with col1:
        st.write("")  # Add an empty line for spacing
        st.image(
            "https://avatars.githubusercontent.com/u/175112039?s=200&v=4", width=65)  # Display the Linkup logo
    with col2:
        st.header("Linkup Configuration")  # Sidebar header
        st.write("Deep Web Search")  # Sidebar sub-header

    st.markdown("[Get your API key](https://app.linkup.so/sign-up)",
                unsafe_allow_html=True)  # Provide a link to get the API key

    linkup_api_key = st.text_input(
        "Enter your Linkup API Key", type="password")  # Input field for the API key (masked)
    if linkup_api_key:  # If the user enters an API key
        st.session_state.linkup_api_key = linkup_api_key  # Store it in session state
        # Update the environment variable
        os.environ["LINKUP_API_KEY"] = linkup_api_key  # Set the API key as an environment variable
        st.success("API Key stored successfully!")  # Show a success message

# Main Chat Interface Header with powered by logos from original code links
col1, col2 = st.columns([6, 1])  # Create two columns for the main header
with col1:
    st.markdown("<h2 style='color: #0066cc;'>🔍 Agentic Deep Researcher</h2>",
                unsafe_allow_html=True)  # Display the app title with custom color
    powered_by_html = """
    <div style='display: flex; align-items: center; gap: 10px; margin-top: 5px;'>
        <span style='font-size: 20px; color: #666;'>Powered by</span>
        <img src="https://cdn.prod.website-files.com/66cf2bfc3ed15b02da0ca770/66d07240057721394308addd_Logo%20(1).svg" width="80"> 
        <span style='font-size: 20px; color: #666;'>and</span>
        <img src="https://framerusercontent.com/images/wLLGrlJoyqYr9WvgZwzlw91A8U.png?scale-down-to=512" width="100">
    </div>
    """
    st.markdown(powered_by_html, unsafe_allow_html=True)  # Show "Powered by" logos
with col2:
    st.button("Clear ↺", on_click=reset_chat)  # Button to clear the chat, calls reset_chat

# Add spacing between header and chat history
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)  # Add vertical space

# Display chat history
for message in st.session_state.messages:  # Loop through each message in the chat history
    with st.chat_message(message["role"]):  # Display the message in the chat interface with the correct role
        st.markdown(message["content"])  # Show the message content

# Accept user input and process the research query
if prompt := st.chat_input("Ask a question about your documents..."):  # Input box for user to type a question
    st.session_state.messages.append({"role": "user", "content": prompt})  # Add user's message to chat history
    with st.chat_message("user"):
        st.markdown(prompt)  # Display the user's message

    if not st.session_state.linkup_api_key:  # If API key is not set
        response = "Please enter your Linkup API Key in the sidebar."  # Prompt user to enter API key
    else:
        with st.spinner("Researching... This may take a moment..."):  # Show a spinner while processing
            try:
                result = run_research(prompt)  # Call the research agent with the user's prompt
                response = result  # Store the result as the response
            except Exception as e:
                response = f"An error occurred: {str(e)}"  # Handle and display any errors

    with st.chat_message("assistant"):
        st.markdown(response)  # Display the assistant's response
    st.session_state.messages.append(
        {"role": "assistant", "content": response})  # Add assistant's response to chat history
