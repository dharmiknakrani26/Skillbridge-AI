import os
import json
import re
from io import BytesIO
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

try:
    from docx import Document
except Exception:
    Document = None

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
except Exception:
    SimpleDocTemplate = None


# =========================================================
# BASIC SETUP
# =========================================================
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="SkillBridge AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SAMPLE DATA
# =========================================================
sample_resume = """Dharmik Nakrani
Entry-Level Data Analyst

Skills:
SQL, Excel, Python, Tableau, Power BI, Data Cleaning, Data Visualization, Dashboarding

Projects:
AEMR Energy Analysis Project
- Used SQL to clean and analyze energy outage data
- Built Tableau visuals to explain outage trends
- Created presentation slides to explain business insights

Portfolio:
Built dashboards and data analytics projects using SQL, Python, and Tableau.
"""

sample_job = """Entry-Level Data Analyst

We are looking for a junior data analyst to help clean, analyze, and visualize business data. The candidate should know SQL, Excel, and dashboard tools such as Tableau or Power BI. Python experience is helpful. Responsibilities include preparing reports, finding trends, creating dashboards, and explaining insights to business teams.
"""


# =========================================================
# SESSION STATE
# =========================================================
if "resume_input" not in st.session_state:
    st.session_state["resume_input"] = ""

if "job_input" not in st.session_state:
    st.session_state["job_input"] = ""

if "last_uploaded_resume_name" not in st.session_state:
    st.session_state["last_uploaded_resume_name"] = ""


# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59, 130, 246, 0.12), transparent 28%),
            radial-gradient(circle at top right, rgba(168, 85, 247, 0.10), transparent 24%),
            linear-gradient(135deg, #020617 0%, #0b1220 45%, #020617 100%);
        color: #f8fafc;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }

    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"] {
        display: none;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617, #0f172a);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    .hero-card {
        padding: 30px 34px;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.22), rgba(109, 40, 217, 0.18));
        border: 1px solid rgba(255, 255, 255, 0.10);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.28);
        margin-bottom: 22px;
    }

    .pill {
        display: inline-block;
        padding: 7px 14px;
        border-radius: 999px;
        background: rgba(59, 130, 246, 0.16);
        border: 1px solid rgba(147, 197, 253, 0.28);
        color: #dbeafe;
        font-size: 13px;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
        white-space: nowrap;
    }

    .hero-title {
        font-size: clamp(2.2rem, 4vw, 4.2rem);
        font-weight: 900;
        line-height: 1.1;
        color: #ffffff;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        font-size: clamp(1rem, 1.5vw, 1.2rem);
        line-height: 1.7;
        color: #dbeafe;
        max-width: 900px;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 20px;
    }

    .feature-card {
        padding: 18px;
        border-radius: 18px;
        background: rgba(15, 23, 42, 0.70);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .feature-title {
        color: #ffffff;
        font-weight: 800;
        font-size: 1.05rem;
        margin-bottom: 6px;
    }

    .feature-text {
        color: #cbd5e1;
        font-size: 0.92rem;
        line-height: 1.55;
    }

    .section-card {
        padding: 20px 22px;
        border-radius: 20px;
        background: rgba(10, 18, 34, 0.72);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 14px 35px rgba(0, 0, 0, 0.18);
        margin-bottom: 14px;
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 8px;
        line-height: 1.25;
    }

    .section-text {
        color: #cbd5e1;
        font-size: 0.98rem;
        line-height: 1.65;
    }

    .stTextArea label,
    .stFileUploader label {
        font-weight: 700 !important;
        color: #e2e8f0 !important;
    }

    .stTextArea textarea {
        border-radius: 16px !important;
        border: 1px solid rgba(148, 163, 184, 0.28) !important;
        background-color: rgba(15, 23, 42, 0.82) !important;
        color: #f8fafc !important;
        font-size: 15px !important;
        padding: 14px !important;
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        padding: 0.82rem 1rem;
        font-weight: 800;
        font-size: 15px;
        border: 1px solid rgba(147, 197, 253, 0.25);
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        box-shadow: 0 10px 26px rgba(59, 130, 246, 0.22);
        transition: 0.2s ease-in-out;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        border: 1px solid rgba(147, 197, 253, 0.40);
    }

    .stDownloadButton > button {
        border-radius: 14px;
        padding: 0.82rem 1rem;
        font-weight: 800;
        border: 1px solid rgba(147, 197, 253, 0.24);
    }

    [data-testid="stMetric"] {
        background: rgba(10, 18, 34, 0.68);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 14px;
        border-radius: 18px;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 30px;
        font-weight: 900;
    }

    [data-testid="stMetricLabel"] {
        color: #cbd5e1;
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        flex-wrap: wrap;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding: 10px 18px;
        background-color: rgba(15, 23, 42, 0.88);
        border: 1px solid rgba(148, 163, 184, 0.16);
    }

    .footer-note {
        text-align: center;
        color: #94a3b8;
        padding: 22px 8px 8px 8px;
        font-size: 14px;
        line-height: 1.6;
    }

    @media (max-width: 900px) {
        .feature-grid {
            grid-template-columns: 1fr;
        }

        .hero-card {
            padding: 22px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================
SKILL_BANK = [
    "SQL",
    "Excel",
    "Python",
    "Tableau",
    "Power BI",
    "Pandas",
    "Data Cleaning",
    "Data Visualization",
    "Dashboard",
    "Reporting",
    "Statistics",
    "Business Intelligence",
    "Power Query",
    "Google Sheets",
    "ETL",
    "Data Analysis",
    "Data Storytelling",
    "Communication",
    "Problem Solving",
    "KPIs",
    "Forecasting",
    "Machine Learning",
    "PowerPoint",
    "Presentation",
    "Jupyter",
    "GitHub",
]


def find_skills(text):
    found = []
    text_lower = text.lower()

    for skill in SKILL_BANK:
        if skill.lower() in text_lower:
            found.append(skill)

    return sorted(list(set(found)))


def make_skill_review(resume_text, job_text):
    resume_skills = find_skills(resume_text)
    job_skills = find_skills(job_text)

    matched = sorted(list(set(resume_skills).intersection(set(job_skills))))
    missing = sorted(list(set(job_skills).difference(set(resume_skills))))

    if len(job_skills) == 0:
        local_score = 0
    else:
        local_score = round((len(matched) / len(job_skills)) * 100)

    return resume_skills, job_skills, matched, missing, local_score


def extract_text_from_upload(uploaded_file):
    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".txt") or file_name.endswith(".md"):
        try:
            return uploaded_file.getvalue().decode("utf-8")
        except Exception:
            return uploaded_file.getvalue().decode("latin-1")

    if file_name.endswith(".pdf"):
        if PdfReader is None:
            st.error("PDF reader is not installed. Run: pip install pypdf")
            return ""

        try:
            pdf_reader = PdfReader(uploaded_file)
            text = ""

            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            return text.strip()
        except Exception as e:
            st.error(f"Could not read PDF file: {e}")
            return ""

    if file_name.endswith(".docx"):
        if Document is None:
            st.error("Word reader is not installed. Run: pip install python-docx")
            return ""

        try:
            document = Document(uploaded_file)
            paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
            return "\n".join(paragraphs).strip()
        except Exception as e:
            st.error(f"Could not read Word file: {e}")
            return ""

    return ""


def extract_json(text):
    try:
        return json.loads(text)
    except Exception:
        pass

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return None


def clean_text_for_pdf(text):
    if text is None:
        return ""

    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def make_pdf_report(data, resume_skills, job_skills, matched, missing, local_score):
    if SimpleDocTemplate is None:
        return None

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "SkillBridgeTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=28,
        spaceAfter=14,
    )

    heading_style = ParagraphStyle(
        "SkillBridgeHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "SkillBridgeNormal",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        spaceAfter=8,
    )

    small_style = ParagraphStyle(
        "SkillBridgeSmall",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        textColor=colors.grey,
        spaceAfter=8,
    )

    story = []

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    story.append(Paragraph("SkillBridge AI Review Report", title_style))
    story.append(Paragraph(f"Generated: {now}", small_style))
    story.append(Paragraph("Human-led and Gemini-powered career fit analysis.", normal_style))
    story.append(Spacer(1, 10))

    score_table_data = [
        ["Review Item", "Result"],
        ["Gemini Fit Score", f"{data.get('fit_score', 'N/A')}/100"],
        ["Skill Match Score", f"{local_score}/100"],
        ["Matched Skills", str(len(matched))],
        ["Missing Skills", str(len(missing))],
    ]

    score_table = Table(score_table_data, colWidths=[2.4 * inch, 3.8 * inch])
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(score_table)

    story.append(Paragraph("Summary", heading_style))
    story.append(Paragraph(clean_text_for_pdf(data.get("summary", "No summary generated.")), normal_style))

    story.append(Paragraph("Skills Review", heading_style))

    skill_rows = [
        ["Category", "Skills"],
        ["Resume Skills", ", ".join(resume_skills) if resume_skills else "No skills found."],
        ["Job Skills", ", ".join(job_skills) if job_skills else "No skills found."],
        ["Matching Skills", ", ".join(matched) if matched else "No matching skills found."],
        ["Missing Skills", ", ".join(missing) if missing else "No missing skills found."],
    ]

    skill_table = Table(skill_rows, colWidths=[1.6 * inch, 4.6 * inch])
    skill_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(skill_table)

    story.append(Paragraph("Resume Improvement Suggestions", heading_style))
    suggestions = data.get("resume_improvements", [])

    if suggestions:
        for item in suggestions:
            story.append(Paragraph(f"• {clean_text_for_pdf(item)}", normal_style))
    else:
        story.append(Paragraph("No suggestions generated.", normal_style))

    story.append(Paragraph("Project Idea to Improve Fit", heading_style))
    project = data.get("project_idea", {})

    if isinstance(project, dict):
        story.append(Paragraph(f"<b>{clean_text_for_pdf(project.get('title', 'Project Idea'))}</b>", normal_style))
        story.append(Paragraph(clean_text_for_pdf(project.get("description", "No description generated.")), normal_style))

        tools = project.get("tools", [])
        if tools:
            story.append(Paragraph(f"<b>Suggested tools:</b> {clean_text_for_pdf(', '.join(tools))}", normal_style))
    else:
        story.append(Paragraph(clean_text_for_pdf(project), normal_style))

    story.append(Paragraph("7-Day Action Plan", heading_style))
    plan = data.get("seven_day_plan", [])

    if plan:
        for item in plan:
            if isinstance(item, dict):
                day = clean_text_for_pdf(item.get("day", "Day"))
                task = clean_text_for_pdf(item.get("task", ""))
                story.append(Paragraph(f"<b>{day}:</b> {task}", normal_style))
            else:
                story.append(Paragraph(f"• {clean_text_for_pdf(item)}", normal_style))
    else:
        story.append(Paragraph("No action plan generated.", normal_style))

    story.append(Paragraph("Honesty Note", heading_style))
    story.append(
        Paragraph(
            clean_text_for_pdf(
                data.get(
                    "honesty_note",
                    "Gemini provides support, but the user makes final decisions."
                )
            ),
            normal_style,
        )
    )

    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "SkillBridge AI is a human-led, Gemini-powered tool. This report is for learning and career preparation support only.",
            small_style,
        )
    )

    doc.build(story)
    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🎯 SkillBridge AI")
    st.markdown("**Built for:** Build with Gemini XPRIZE")
    st.markdown("**Style:** Human-led + Gemini-powered")

    st.divider()

    st.markdown("### Tool checks")
    st.markdown(
        """
        - Resume upload
        - Resume fit score
        - Matching skills
        - Missing skills
        - Resume improvements
        - Project recommendation
        - 7-day action plan
        - PDF review report
        """
    )

    st.divider()

    st.markdown("### Safe build rule")
    st.info("Do not paste private information like SSN, full address, or API keys.")


# =========================================================
# HERO SECTION
# =========================================================
st.markdown(
    """
    <div class="hero-card">
        <div>
            <span class="pill">Build with Gemini</span>
            <span class="pill">Career Analytics</span>
            <span class="pill">Resume Upload</span>
            <span class="pill">PDF Report</span>
        </div>
        <div class="hero-title">🎯 SkillBridge AI</div>
        <div class="hero-subtitle">
            A professional AI-powered career assistant for entry-level job seekers.
            Upload or paste a resume, compare it with a job description, review skill gaps,
            and download a clean PDF improvement report.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FEATURE CARDS
# =========================================================
st.markdown(
    """
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-title">📄 Resume Upload</div>
            <div class="feature-text">
                Upload a PDF, Word DOCX, TXT, or Markdown resume file.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-title">🧠 Gemini Review</div>
            <div class="feature-text">
                Gemini reviews resume fit, missing skills, and practical improvement steps.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-title">📥 PDF Report</div>
            <div class="feature-text">
                Download a professional review report to save, share, or improve later.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TOP ACTION BUTTONS
# These buttons run before text boxes, so no session_state conflict.
# =========================================================
action_col1, action_col2, action_col3 = st.columns([1, 1, 3])

with action_col1:
    if st.button("🧪 Use Sample", use_container_width=True):
        st.session_state["resume_input"] = sample_resume
        st.session_state["job_input"] = sample_job
        st.session_state["last_uploaded_resume_name"] = ""
        st.rerun()

with action_col2:
    if st.button("🧹 Clear All", use_container_width=True):
        st.session_state["resume_input"] = ""
        st.session_state["job_input"] = ""
        st.session_state["last_uploaded_resume_name"] = ""
        st.rerun()


# =========================================================
# INPUT SECTION
# =========================================================
left_col, right_col = st.columns(2)

with left_col:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Resume Input</div>
            <div class="section-text">
                Upload your resume or paste text manually. Word support is for .docx files.
                If you have an old .doc file, save it as PDF or .docx first.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_resume = st.file_uploader(
        "Upload resume file",
        type=["pdf", "docx", "txt", "md"],
        help="Supported file types: PDF, DOCX, TXT, MD"
    )

    if uploaded_resume is not None:
        st.caption(f"Selected file: {uploaded_resume.name}")

        if st.button("📄 Load Uploaded Resume", use_container_width=True):
            extracted_text = extract_text_from_upload(uploaded_resume)

            if extracted_text:
                st.session_state["resume_input"] = extracted_text
                st.session_state["last_uploaded_resume_name"] = uploaded_resume.name
                st.success("Resume loaded into the text box.")
                st.rerun()
            else:
                st.error("Could not read text from the uploaded file.")

    if st.session_state["last_uploaded_resume_name"]:
        st.success(f"Loaded resume: {st.session_state['last_uploaded_resume_name']}")

    st.text_area(
        "Resume text",
        key="resume_input",
        height=320,
        placeholder="Paste resume text here..."
    )

with right_col:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Job Description Input</div>
            <div class="section-text">
                Paste the job description. SkillBridge AI compares the role requirements with your resume.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.text_area(
        "Job description",
        key="job_input",
        height=405,
        placeholder="Paste job description here..."
    )


# =========================================================
# ANALYZE BUTTON
# =========================================================
button_col1, button_col2 = st.columns([1, 4])

with button_col1:
    analyze_button = st.button("🚀 Analyze Fit", use_container_width=True)


# =========================================================
# ANALYSIS SECTION
# =========================================================
if analyze_button:
    resume_text = st.session_state["resume_input"]
    job_text = st.session_state["job_input"]

    if not api_key:
        st.error("Gemini API key not found. Please check your .env file.")
    elif not resume_text.strip() or not job_text.strip():
        st.warning("Please upload/paste resume text and paste the job description.")
    else:
        resume_skills, job_skills, matched, missing, local_score = make_skill_review(
            resume_text,
            job_text
        )

        prompt = f"""
You are helping an entry-level job seeker.

Important rules:
- Use simple human language.
- Be honest.
- Do not exaggerate.
- Do not say the user has a skill unless it appears in the resume.
- Give practical advice.
- Return ONLY valid JSON.
- No markdown outside JSON.

Return this JSON structure:
{{
  "fit_score": 0,
  "summary": "short paragraph",
  "top_matching_skills": ["skill 1", "skill 2"],
  "missing_skills": ["skill 1", "skill 2"],
  "resume_improvements": ["suggestion 1", "suggestion 2", "suggestion 3"],
  "project_idea": {{
    "title": "project title",
    "description": "project description",
    "tools": ["tool 1", "tool 2"]
  }},
  "seven_day_plan": [
    {{"day": "Day 1", "task": "task"}},
    {{"day": "Day 2", "task": "task"}},
    {{"day": "Day 3", "task": "task"}},
    {{"day": "Day 4", "task": "task"}},
    {{"day": "Day 5", "task": "task"}},
    {{"day": "Day 6", "task": "task"}},
    {{"day": "Day 7", "task": "task"}}
  ],
  "honesty_note": "short note"
}}

Resume:
{resume_text}

Job Description:
{job_text}
"""

        with st.spinner("Gemini is reviewing the resume and job description..."):
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )

            raw_text = response.text
            data = extract_json(raw_text)

        if data is None:
            st.error("Gemini returned text, but it was not clean JSON. Showing raw result below.")
            st.write(raw_text)
        else:
            st.markdown("## ✅ Review Result")

            metric1, metric2, metric3, metric4 = st.columns(4)

            with metric1:
                st.metric("Gemini Fit Score", f"{data.get('fit_score', 'N/A')}/100")

            with metric2:
                st.metric("Skill Match Score", f"{local_score}/100")

            with metric3:
                st.metric("Matched Skills", len(matched))

            with metric4:
                st.metric("Missing Skills", len(missing))

            try:
                fit_value = int(data.get("fit_score", 0))
                st.progress(min(fit_value, 100) / 100)
            except Exception:
                pass

            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                [
                    "📌 Summary",
                    "📋 Skills Review",
                    "🛠 Resume Tips",
                    "📅 Action Plan",
                    "📥 PDF Report",
                ]
            )

            with tab1:
                st.markdown("### Short Summary")
                st.write(data.get("summary", "No summary generated."))

                st.markdown("### Honesty Note")
                st.info(
                    data.get(
                        "honesty_note",
                        "Gemini provides support, but the user makes final decisions."
                    )
                )

                st.markdown("### Project Idea to Improve Fit")
                project = data.get("project_idea", {})

                if isinstance(project, dict):
                    st.markdown(f"**{project.get('title', 'Project idea')}**")
                    st.write(project.get("description", "No description generated."))

                    tools = project.get("tools", [])
                    if tools:
                        st.markdown("**Suggested tools:** " + ", ".join(tools))
                else:
                    st.write(project)

            with tab2:
                st.markdown("### Clean Skills Review")

                skill_table = pd.DataFrame(
                    [
                        {
                            "Category": "Resume Skills Found",
                            "Count": len(resume_skills),
                            "Details": ", ".join(resume_skills) if resume_skills else "No skills found",
                        },
                        {
                            "Category": "Job Skills Found",
                            "Count": len(job_skills),
                            "Details": ", ".join(job_skills) if job_skills else "No skills found",
                        },
                        {
                            "Category": "Matching Skills",
                            "Count": len(matched),
                            "Details": ", ".join(matched) if matched else "No matching skills found",
                        },
                        {
                            "Category": "Missing Skills",
                            "Count": len(missing),
                            "Details": ", ".join(missing) if missing else "No missing skills found",
                        },
                    ]
                )

                st.dataframe(skill_table, use_container_width=True, hide_index=True)

                st.caption(
                    "This is a simple keyword-based skills review. Gemini gives the deeper written explanation."
                )

            with tab3:
                st.markdown("### Resume Improvement Suggestions")
                suggestions = data.get("resume_improvements", [])

                if suggestions:
                    for i, suggestion in enumerate(suggestions, start=1):
                        st.markdown(f"**{i}.** {suggestion}")
                else:
                    st.write("No suggestions generated.")

            with tab4:
                st.markdown("### 7-Day Career Action Plan")
                plan = data.get("seven_day_plan", [])

                if plan:
                    for item in plan:
                        if isinstance(item, dict):
                            st.markdown(f"**{item.get('day', '')}:** {item.get('task', '')}")
                        else:
                            st.markdown(f"- {item}")
                else:
                    st.write("No action plan generated.")

            with tab5:
                st.markdown("### Download PDF Review Report")
                st.write(
                    "This PDF includes the fit score, skills review, Gemini summary, resume suggestions, project idea, and 7-day action plan."
                )

                pdf_bytes = make_pdf_report(
                    data,
                    resume_skills,
                    job_skills,
                    matched,
                    missing,
                    local_score
                )

                if pdf_bytes is None:
                    st.error("PDF library not installed. Run: pip install reportlab")
                else:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_bytes,
                        file_name="skillbridge_ai_review_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div class="footer-note">
        SkillBridge AI is human-led and Gemini-powered. It helps users make better career decisions,
        but the final choice stays with the user.
    </div>
    """,
    unsafe_allow_html=True
)