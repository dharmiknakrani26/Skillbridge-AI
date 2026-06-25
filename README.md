# SkillBridge AI

**SkillBridge AI** is a human-led, Gemini-powered resume and job fit review web app for entry-level job seekers.

The app helps users upload or paste a resume, compare it with a job description, identify skill gaps, receive practical improvement suggestions, and download a professional PDF review report.

## Live Demo

https://skillbridge-ai-dharmik.streamlit.app/

## Source Code

https://github.com/dharmiknakrani26/Skillbridge-AI

## Built For

**Build with Gemini XPRIZE**

## Project Overview

Many entry-level job seekers struggle to understand why their resume does not match a job description. SkillBridge AI helps solve this problem by giving users a clear and simple career fit review.

Users can upload a resume or paste resume text, paste a job description, and receive a structured review powered by Gemini. The goal is to help job seekers understand their current fit, missing skills, resume improvement areas, and next career steps.

## Key Features

* Resume upload support for PDF, DOCX, TXT, and Markdown files
* Manual resume text input
* Job description input
* Gemini-powered resume and job fit analysis
* Job fit score out of 100
* Skill match score
* Matching skills review
* Missing skills review
* Resume improvement suggestions
* Project recommendation to improve job readiness
* 7-day career action plan
* Professional PDF report download
* Clean and beginner-friendly web interface

## How It Works

1. The user uploads or pastes a resume.
2. The user pastes a job description.
3. SkillBridge AI compares the resume with the job requirements.
4. Gemini generates a structured career fit review.
5. The app displays fit score, skill gaps, resume tips, and action plan.
6. The user can download the full review as a PDF report.

## Tech Stack

* Python
* Streamlit
* Gemini API
* Google GenAI SDK
* Pandas
* pypdf
* python-docx
* ReportLab
* python-dotenv

## AI Usage

SkillBridge AI is **human-led and Gemini-powered**.

### Human-led work includes:

* Project idea
* Product direction
* User flow
* Web app design decisions
* Testing
* Screenshots
* GitHub setup
* Devpost submission planning

### Gemini-powered work includes:

* Resume and job description analysis
* Fit score explanation
* Skill gap review
* Resume improvement suggestions
* Project recommendation
* 7-day action plan generation

The user makes the final decision. Gemini is used as a support tool for analysis and recommendations.

## Safety and Privacy

SkillBridge AI is designed for career preparation support.

Users should avoid uploading private information such as:

* Social Security numbers
* Full home address
* Passwords
* API keys
* Sensitive personal documents

The Gemini API key is stored locally in a `.env` file during local development. The `.env` file is protected by `.gitignore` and should never be uploaded to GitHub.

For the deployed Streamlit app, the Gemini API key is stored securely using Streamlit Secrets.

## Local Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/dharmiknakrani26/Skillbridge-AI.git
cd Skillbridge-AI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

For Windows:

```bash
.venv\Scripts\activate
```

For Mac or Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create a `.env` file

Create a file named `.env` in the project folder and add:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 6. Run the app locally

```bash
streamlit run app.py
```

The app will open in the browser at:

```bash
http://localhost:8501/
```

## Project Structure

```text
Skillbridge-AI/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── Idea Notes/
├── Research/
├── Screenshots/
├── User Feedback/
├── Revenue Proof/
└── Final Submission/
```

## Current Project Status

MVP completed.

The current version includes:

* Resume upload
* Resume text input
* Job description input
* Gemini-powered review
* Clean skills review table
* PDF report download
* Public Streamlit deployment
* GitHub documentation

## Future Improvements

Planned future improvements include:

* User login
* Saved report history
* More resume format support
* Better skill extraction
* Dashboard for common job market skills
* Stripe payment or waitlist system
* User feedback collection form
* Google Cloud deployment option

## Author

**Dharmik Nakrani**

GitHub: https://github.com/dharmiknakrani26