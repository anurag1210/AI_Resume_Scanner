import streamlit as st
from resume_processor import load_resume, analyze_resume, store_to_vectorstore, run_self_query
import os

st.set_page_config(page_title="AI Resume Analyzer", page_icon=":briefcase:", layout="wide")
st.title("AI Resume Analyzer")
st.markdown("Upload a resume and a job description to analyze the candidate's suitability")

# Initialise session state
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'report' not in st.session_state:
    st.session_state.report = None

job_desc = st.text_area('Enter Job Description', height=200)
uploaded_file = st.file_uploader("Upload Resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if st.button("Analyze and Store") and uploaded_file and job_desc:
    temp_file_path = uploaded_file.name
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Processing resume ..."):
        docs = load_resume(temp_file_path)
        report = analyze_resume(docs, job_desc)
        store_to_vectorstore(docs)
        
        # Save to session state ← key fix!
        st.session_state.analyzed = True
        st.session_state.report = report

# Show results OUTSIDE the button block — persists across reruns!
if st.session_state.analyzed:
    st.success("Resume analyzed and stored successfully!")
    st.subheader("AI Resume Summary")
    st.write(st.session_state.report)
    st.download_button(
        "Download Analysis Report",
        data=st.session_state.report,
        file_name="resume_analysis.txt"
    )

    st.divider()

    st.subheader("Query your resume data")
    query = st.text_input("Enter your query about resume")

    if st.button("Search Resume") and query:
        with st.spinner("Searching resume ..."):
            results = run_self_query(query)
            if results:
                if isinstance(results, str):
                    st.write(results)
                else:
                    for i, res in enumerate(results, 1):
                        st.markdown(f"**Result {i}:**")
                        st.write(
                            res.page_content.strip() 
                            if hasattr(res, 'page_content') 
                            else str(res).strip()
                        )
            else:
                st.warning("No results found.")