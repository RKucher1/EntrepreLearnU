import streamlit as st
import openai
import os
from dotenv import load_dotenv
import yake

# Import openai token
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set page configuration
st.set_page_config(
    page_title="EntrepreLearnU Bot",
    page_icon="🕴️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("EntrepreLearnU Bot 🕴️")
st.subheader("Welcome to EntrepreLearnU Bot, use the chat feature below to search for your business questions.")

# Function to summarize the chat history
def summarize_chat_history(chat_history):
    # Concatenate all messages into a single text
    text = " ".join([m['content'] for m in chat_history])
    # Use YAKE to extract keywords
    kw_extractor = yake.KeywordExtractor()
    keywords = kw_extractor.extract_keywords(text)
    # Use the top 5 keywords as the summary
    summary = " ".join([kw[0] for kw in keywords[:5]])
    return summary

# Initialize the chat history if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.header("Personalization")
    user_interest = st.selectbox("Select your interest", ["Marketing", "Finance", "Strategy", "Operations", "HR"])
    business_model = st.selectbox("What is your business model?", ["B2B", "B2C", "SaaS", "E-commerce", "Subscription", "Freemium", "Marketplace", "Direct Sales", "Advertising"])
    
    if st.button("Clear chat history"):
        st.session_state.chat_history = []
    
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file is not None:
        st.write("PDF uploaded successfully!")

    # Feedback
    if st.button("Provide Feedback"):
        feedback = st.text_input("What do you think about the advice?")
        if feedback:
            st.write("Thank you for your feedback!")

# Setup the streamlit application
message = st.text_input("Ask a question here", value=st.session_state.message)

if message:
    # Add the new message to the chat history
    st.session_state.chat_history.append({"role": "user", "content": message})
    
    # Clear the message
    st.session_state.message = ""
    
    # Summarize the chat history
    summarized_chat_history = summarize_chat_history(st.session_state.chat_history)
    
    # Calculate the total tokens in the user's messages
    user_tokens = sum(len(m['content'].split()) for m in summarized_chat_history)
    
    # Calculate the completion tokens
    completion_tokens = 4096 - user_tokens - 1  # Subtract an additional token for safety
    
    # Prepare the messages for the model
    system_message = {
        "Marketing": f"You are a helpful assistant that specializes in marketing. You can provide insights on marketing strategies, market analysis, customer acquisition, and brand management for {business_model} businesses.",
        "Finance": f"You are a helpful assistant that specializes in finance. You can provide insights on financial planning, funding options, budgeting, and financial analysis for {business_model} businesses.",
        "Strategy": f"You are a helpful assistant that specializes in business strategy. You can provide insights on business models, strategic planning, competitive analysis, and business development for {business_model} businesses.",
        "Operations": f"You are a helpful assistant that specializes in operations. You can provide insights on operational management, process improvement, supply chain management, and quality control for {business_model} businesses.",
        "HR": f"You are a helpful assistant that specializes in human resources. You can provide insights on hiring, employee management, organizational culture, and employee development for {business_model} businesses."
    }[user_interest]
    messages_for_model = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": message}
    ]
    
    # If there are previous responses in the chat history, add the last one to the messages for the model
    if len(summarized_chat_history) > 1:
        last_response = summarized_chat_history[-2]
        if last_response['role'] == 'assistant':
            messages_for_model.append(last_response)
    
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-0613",
      messages=messages_for_model,
      max_tokens=min(4000, completion_tokens)  # Ensure the total tokens are below 4096
    )
    st.session_state.chat_history.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
    st.write(response['choices'][0]['message']['content'])