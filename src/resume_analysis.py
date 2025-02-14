"""
Module: resume_analysis
Purpose: Evaluate candidate resumes against job descriptions and generate interview Q&A.

"""

import streamlit as st
import json
import pandas as pd
import os
from utils import fetch_text_content, retrieve_contact_details
import authentication
from openai import OpenAI

# Initialize AI client using environment variable for API key.
ai_instance = OpenAI(api_key=os.environ.get("API_KEY"))

def display_resume_dashboard():
    """
    Displays the main dashboard for resume analysis.
    Provides fields for job description, resume uploads, and options for analysis and Q&A generation.
    
    """
    jd_text = ""
    left_col, right_col = st.columns(2)
    with left_col:
        st.write("### Input Job Description:")
        jd_text = st.text_area("Job Description", height=200)
    with right_col:
        st.write("### Upload Candidate Resumes (PDF, DOCX, TXT):")
        upload_files = st.file_uploader(
            "Drag or choose resume files",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="resume_uploads"
        )
    analyze_trigger = st.button("Evaluate Resumes", type="primary", disabled=not (jd_text and upload_files))
    
    # Initialize session state stores.
    if "results" not in st.session_state:
        st.session_state.results = []
    if "resume_texts" not in st.session_state:
        st.session_state.resume_texts = {}
    if "qa_output" not in st.session_state:
        st.session_state.qa_output = None
    if "selected_candidate" not in st.session_state:
        st.session_state.selected_candidate = None

    if analyze_trigger:
        with st.spinner("Assessing submitted resumes..."):
            st.session_state.results = []
            st.session_state.resume_texts = {}
            for resume in upload_files:
                try:
                    text_content = fetch_text_content(resume)
                    eval_output = perform_resume_evaluation(jd_text, text_content)
                    score, match_status, skills_list, rationale, candidate_name, email_addr = parse_evaluation(eval_output)
                    st.session_state.results.append({
                        "Candidate Name": candidate_name,
                        "Email": email_addr,
                        "Score": score,
                        "Match": match_status,
                        "Skills Found": skills_list,
                        "Rationale": rationale,
                    })
                    st.session_state.resume_texts[candidate_name] = text_content
                except Exception as err:
                    st.error(f"Failed to process {resume.name}: {err}")
        if st.session_state.results:
            authentication.log_usage(st.session_state.user_info['email'], len(upload_files))
    
    if st.session_state.results:
        # Sort candidates by score in descending order.
        sorted_candidates = sorted(st.session_state.results, key=lambda x: x["Score"], reverse=True)
        df_candidates = pd.DataFrame(sorted_candidates)
        st.subheader("Candidates Ranked by Evaluation Score")
        st.dataframe(df_candidates, height=400)
        csv_data = df_candidates.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV of Evaluations",
            data=csv_data,
            file_name="evaluation_results.csv",
            mime="text/csv"
        )
        st.subheader("Generate Interview Q&A")
        candidate_names = [entry["Candidate Name"] for entry in sorted_candidates]
        selected = st.selectbox(
            "Select a candidate for interview Q&A generation:",
            candidate_names,
            index=candidate_names.index(st.session_state.selected_candidate) if st.session_state.selected_candidate else 0
        )
        st.session_state.selected_candidate = selected
        if "qa_data" not in st.session_state:
            st.session_state.qa_data = []
        if selected:
            candidate_resume = st.session_state.resume_texts.get(selected, "")
            if candidate_resume:
                if st.button("Create Interview Q&A"):
                    with st.spinner("Generating Q&A..."):
                        st.session_state.qa_data = generate_interview_qa(jd_text, candidate_resume)
                if st.session_state.qa_data:
                    st.write("### Interview Questions & Suggested Answers:")
                    st.write(st.session_state.qa_data)

def perform_resume_evaluation(job_desc, resume_content):
    """
    Constructs a prompt for evaluating a candidate's resume against the job description
    and calls the AI service to retrieve evaluation details.

    Args:
        job_desc (str): Job description text.
        resume_content (str): Text extracted from the candidate's resume.

    Returns:
        dict: A dictionary containing evaluation metrics and feedback.
    """
    if not resume_content.strip():
        return {"error": "The resume content is empty."}
    
    prompt_text = f"""
You are a recruitment expert responsible for assessing candidate qualifications.
Focus on key competencies mentioned in both the job description and resume.

### Job Description:
{job_desc}

### Candidate Resume:
{resume_content}

**Evaluation Breakdown (Total out of 100):**
1. Core Technical Skills (60%):
   - Specific project details (45%)
   - General technical knowledge (15%)
2. Professional Experience (10%)
3. Educational Background (20%)
4. Geographic Relevance (5%)
5. Additional Certifications (5%)

**Result:**
- "Match: Yes" for scores 70 or above.
- "Match: No" for scores below 70.

Provide the result in the JSON format:
{{
  "Candidate Name": "Candidate Name",
  "Email": "Email Address",
  "Score": NumericScore,
  "Match": "Yes/No",
  "Skills Found": ["List", "of", "skills"],
  "Rationale": "Short explanation"
}}
"""
    try:
        ai_response = ai_instance.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are a top-tier recruitment evaluation assistant."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=1000,
            temperature=0,
            response_format={"type": "json_object"}
        )
        response_str = ai_response.choices[0].message.content
        return json.loads(response_str)
    except Exception as e:
        return {"error": f"AI evaluation failed: {e}"}

def parse_evaluation(evaluation_data):
    """
    Parses the evaluation output from the AI service and returns the evaluation parameters.
    
    Args:
        evaluation_data (dict): The raw evaluation response from the AI service.
    
    Returns:
        tuple: (score, match status, list of skills, rationale, candidate name, email)
    """
    try:
        if "error" in evaluation_data:
            return 0, "No", [], "", "Unknown", "N/A"
        return (
            int(evaluation_data.get("Score", 0)),
            evaluation_data.get("Match", "No"),
            evaluation_data.get("Skills Found", []),
            evaluation_data.get("Rationale", "No explanation provided."),
            evaluation_data.get("Candidate Name", "Unknown"),
            evaluation_data.get("Email", "N/A")
        )
    except Exception as parse_err:
        return 0, "No", [], f"Error during parsing: {parse_err}", "Unknown", "N/A"

def generate_interview_qa(job_desc, resume_content):
    """
    Generates interview questions and model answers based on job and resume details.

    Args:
        job_desc (str): The job description text.
        resume_content (str): Text extracted from the candidate's resume.
    
    Returns:
        str: A formatted string containing interview questions and corresponding answers.
    """
    qa_prompt = f"""
You are an AI consultant in recruitment. Generate 10 concise technical interview questions with model answers based on the information provided.

### Job Description:
{job_desc}

### Candidate Resume:
{resume_content}

Instructions:
- The questions should target essential technical areas from the job description.
- Answers should be short and informative.

Return a JSON output with the structure:
{{
  "questions": [
    {{"question": "Question 1", "answer": "Answer 1"}},
    ...
  ]
}}
"""
    try:
        qa_response = ai_instance.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are an experienced recruitment consultant."},
                {"role": "user", "content": qa_prompt}
            ],
            max_tokens=1500,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        qa_json = json.loads(qa_response.choices[0].message.content)
        questions = qa_json.get("questions", [])
        out_lines = []
        for idx, entry in enumerate(questions):
            out_lines.append(f"**{idx + 1}. {entry['question']}**")
            out_lines.append(f"Suggested Answer: {entry['answer']}\n")
        return "\n".join(out_lines)
    except Exception as ex:
        return f"Error generating interview Q&A: {ex}"
