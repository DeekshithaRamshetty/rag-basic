import streamlit as st
import PyPDF2
import google.generativeai as genai
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="PDF Q&A with Gemini",
    page_icon="📚",
    layout="wide"
)

# Set your Gemini API key here
API_KEY = "AIzaSyCIJq2jtauQ2xxyd9rS87pwX4nK4-rWbHQ"
genai.configure(api_key=API_KEY)

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def ask_gemini(question, context):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content([context, question])
    return response.text

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {text-align: center; color: #1E88E5; margin-bottom: 30px;}
    .stButton>button {background-color: #1E88E5; color: white;}
    .chat-message {padding: 15px; border-radius: 10px; margin-bottom: 10px;}
    .user-message {background-color: #E3F2FD; border-left: 5px solid #1E88E5;}
    .bot-message {background-color: #F5F5F5; border-left: 5px solid #4CAF50;}
    .timestamp {color: #9E9E9E; font-size: 12px; margin-bottom: 5px;}
    .file-info {padding: 10px; background-color: #F1F8E9; border-radius: 5px; margin-top: 10px;}
</style>
""", unsafe_allow_html=True)

# App header with improved styling
st.markdown("<h1 class='main-header'>📚 PDF Q&A with Gemini RAG</h1>", unsafe_allow_html=True)

# Create a sidebar for file upload and information
with st.sidebar:
    st.markdown("### 📄 Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info(
        "This application allows you to upload a PDF document and ask questions about its content. "
        "The app uses Google's Gemini AI to provide accurate answers based on the document content."
    )

pdf_text = ""
pdf_name = ""

if uploaded_file:
    with st.spinner("📄 Processing PDF document..."):
        pdf_text = extract_text_from_pdf(uploaded_file)
        pdf_name = uploaded_file.name
    
    st.success(f"✅ '{pdf_name}' successfully processed!")
    
    # Display file information
    with st.expander("📋 Document Information"):
        st.markdown(f"<div class='file-info'>"  
                    f"<b>File:</b> {pdf_name}<br>"  
                    f"<b>Size:</b> {round(len(uploaded_file.getvalue())/1024, 2)} KB<br>"  
                    f"<b>Text Length:</b> {len(pdf_text)} characters"  
                    f"</div>", unsafe_allow_html=True)

if pdf_text:
    st.markdown("### 💬 Chat with your Document")
    
    # Initialize session state for chat history
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []
    
    # Create two columns for the input area
    col1, col2 = st.columns([5, 1])
    
    with col1:
        question = st.text_input("Ask a question about your document:", key="question_input")
    
    with col2:
        ask_button = st.button("Ask 🔍")
    
    # Process the question when the button is clicked or Enter is pressed
    if ask_button or (question and question != st.session_state.get("last_question", "")):
        if question:  # Ensure question is not empty
            st.session_state.last_question = question
            
            with st.spinner("🤔 Gemini is thinking..."):
                answer = ask_gemini(question, pdf_text)
                timestamp = datetime.now().strftime("%H:%M:%S")
                
            # Add to history with timestamp
            st.session_state.qa_history.append({
                "question": question,
                "answer": answer,
                "timestamp": timestamp
            })
            
            # Clear the input box after submission
            
    
    # Display a divider before the chat history
    if st.session_state.qa_history:
        st.markdown("---")
        st.markdown("### 📜 Conversation History")
    
    # Display chat history in reverse order (newest first)
    for qa in reversed(st.session_state.qa_history):
        # User question with styling
        st.markdown(f"<div class='timestamp'>🕒 {qa.get('timestamp', 'Now')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-message user-message'>"
                    f"<b>You:</b> {qa['question']}"
                    f"</div>", unsafe_allow_html=True)
        
        # AI answer with styling
        st.markdown(f"<div class='chat-message bot-message'>"
                    f"<b>Gemini:</b> {qa['answer']}"
                    f"</div>", unsafe_allow_html=True)
        
        # Add some space between QA pairs
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Add a clear button at the bottom if there's history
    if st.session_state.qa_history:
        if st.button("Clear Conversation"):
            st.session_state.qa_history = []
            
else:
    # Show a welcome message when no PDF is uploaded
    st.markdown("""
    ### 👋 Welcome to PDF Q&A!
    
    To get started:
    1. Upload a PDF document using the sidebar on the left
    2. Wait for the document to be processed
    3. Ask questions about the document content
    
    The AI will analyze the document and provide relevant answers based on the content.
    """)
