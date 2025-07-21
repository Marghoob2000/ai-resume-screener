import streamlit as st
from core.matcher import get_ranked_resumes
import pdfplumber
import os
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="🤖",
    layout="wide"
)

# --- Mock Resume Class (to work with your existing matcher) ---
# This mimics the Django Resume object so we don't have to change your matcher.py
class MockResume:
    def __init__(self, title, text):
        self.title = title
        self.extracted_text = text

# --- Main App ---
st.title("🤖 AI-Powered Resume Screener")
st.write("Upload a job description and multiple resumes to see candidates ranked by relevance.")

# --- API Key Input ---
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your Google AI API Key", type="password")

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
else:
    st.sidebar.warning("Please enter your Google AI API Key to proceed.")
    st.stop()


# --- Input Columns ---
col1, col2 = st.columns(2)

with col1:
    st.header("Job Description")
    job_description_text = st.text_area("Paste the full job description here:", height=300)

with col2:
    st.header("Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload candidate resumes (PDF files only)",
        type="pdf",
        accept_multiple_files=True
    )


# --- Processing and Ranking ---
if st.button("Rank Resumes", type="primary"):
    if not job_description_text:
        st.error("Please provide a job description.")
    elif not uploaded_files:
        st.error("Please upload at least one resume.")
    else:
        with st.spinner("Analyzing resumes... This may take a moment."):
            resumes_list = []
            for uploaded_file in uploaded_files:
                try:
                    # To read the uploaded file in memory
                    bytes_data = BytesIO(uploaded_file.getvalue())
                    with pdfplumber.open(bytes_data) as pdf:
                        text = "".join(page.extract_text() or "" for page in pdf.pages)
                        # Create a mock resume object
                        resumes_list.append(MockResume(title=uploaded_file.name, text=text))
                except Exception as e:
                    st.warning(f"Could not read {uploaded_file.name}. Skipping. Error: {e}")

            if resumes_list:
                # Call your existing matching logic
                ranked_resumes = get_ranked_resumes(job_description_text, resumes_list)

                st.success("Analysis complete! Here are the ranked results:")

                for i, (resume, score) in enumerate(ranked_resumes):
                    st.write(f"**{i+1}. {resume.title}**")
                    st.progress(score, text=f"Match Score: {score:.2f}")
            else:
                st.error("No valid resumes could be processed.")