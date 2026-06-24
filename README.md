# AI Job Application Copilot

AI Job Application Copilot is a beta web application that helps job seekers compare their resume with a job description and understand how well their profile matches a role.

The application allows users to upload a resume, paste a job description, get a resume match score, identify missing skills, receive resume improvement suggestions, view similar role suggestions, get company recommendations, see live job listings, and download a resume analysis report.

This project was built as a hands-on AI Engineering portfolio project to understand how real AI applications are designed, built, deployed, and improved step by step.

---

## Live Demo

Application URL: https://ai-job-application-copilot.streamlit.app/

GitHub Repository: https://github.com/KavyaSinguru02/ai-job-application-copilot

---

## Current Status

This project is currently in **beta version**.

It is deployed and available for testing.

Users should avoid uploading highly sensitive personal information during beta testing.

---

## Why I Built This Project

When I started hearing more about AI and how it is becoming the future, I became curious about how AI applications are actually built.

I started learning Python, but I realized that only watching videos or doing small practice tasks was not enough.

So I decided to build a real project step by step.

This project helped me connect multiple concepts together:

* Python
* Backend APIs
* Frontend UI
* Authentication
* Resume PDF parsing
* LLM integration
* Embeddings
* Vectors
* RAG
* Vector database
* PDF report generation
* Live job market API integration
* Cloud deployment

The process of building this application also helped me gain practical exposure to free-tier and beginner-friendly tools for deploying frontend and backend applications.

---

## Problem Statement

When applying for jobs, candidates often struggle with questions like:

* Does my resume match this job description?
* What percentage does my resume match?
* What skills am I missing?
* What keywords should I include?
* How can I improve my resume for this specific role?
* What similar roles can I apply for?
* Which companies may be suitable for this type of role?
* Are there any live job openings for this role?
* Can I quickly download a useful report before applying?

AI Job Application Copilot tries to solve these problems using AI.

---

## Application Flow

```text
User signs up or logs in
        ↓
User uploads resume PDF
        ↓
User pastes job description
        ↓
Backend extracts resume text
        ↓
Resume and job description are analyzed
        ↓
Resume sections are converted into embeddings
        ↓
Vector search retrieves relevant resume evidence
        ↓
AI calculates match score and missing skills
        ↓
AI generates resume improvement suggestions
        ↓
Adzuna fetches live job/company data when available
        ↓
AI suggests similar roles and target companies
        ↓
User downloads a resume analysis PDF report
        ↓
Admin can view basic usage analytics
```

---

## Main Features

* User signup and login
* Resume PDF upload
* Job description input
* Resume text extraction
* AI-based resume and job description analysis
* Dynamic skill extraction
* Resume match percentage
* ATS keyword score
* Semantic fit score
* Embeddings-based semantic matching
* Qdrant Cloud vector database integration
* Basic RAG-based resume evidence retrieval
* Missing skills detection
* Resume improvement suggestions
* ATS-friendly keyword suggestions
* Optimized resume headline
* Optimized professional summary
* Suggested resume bullet points
* Similar role recommendations
* AI-based company recommendations
* Live job listings using Adzuna API
* Live top company suggestions using Adzuna API
* LinkedIn search keyword suggestions
* Downloadable PDF report
* Admin-only basic analytics dashboard

---

## Tech Stack

### Backend

* Python
* FastAPI
* Gemini API
* Pydantic
* pdfplumber
* ReportLab
* Qdrant Cloud
* Supabase
* Adzuna API

### Frontend

* Streamlit

### Authentication and Analytics

* Supabase Auth
* Supabase database for basic usage tracking

### Deployment and Hosting

* Render for backend deployment
* Streamlit Community Cloud for frontend deployment
* Supabase for authentication and analytics
* Qdrant Cloud for vector database
* Gemini API for LLM and embeddings
* Adzuna API for live job-market data

---

## Deployment Architecture

```text
User Browser
    ↓
Streamlit Frontend
    ↓
Render-hosted FastAPI Backend
    ↓
Supabase Authentication
    ↓
Resume PDF Parser
    ↓
Gemini Embeddings
    ↓
Qdrant Cloud Vector Database
    ↓
Gemini LLM Analysis
    ↓
Adzuna Live Job Data
    ↓
PDF Report Generator
    ↓
Supabase Analytics
```

---

## Where AI Engineering Concepts Are Used

### 1. Python

Python is the main programming language used in the backend.

It is used for:

* API development
* Resume text extraction
* AI model calls
* Embedding generation
* Vector search flow
* RAG evidence processing
* Live job API integration
* PDF report generation
* Authentication validation
* Analytics saving

---

### 2. FastAPI

FastAPI is used to build the backend APIs.

Main endpoints include:

```text
GET  /
GET  /health
POST /analyze
POST /generate-report
GET  /admin/stats
```

FastAPI handles:

* Resume upload
* Job description input
* Authentication check
* Resume analysis
* Adzuna job data retrieval
* PDF report generation
* Admin analytics

---

### 3. Streamlit

Streamlit is used to build the frontend interface.

It allows users to:

* Sign up and log in
* Upload resume PDF
* Paste job description
* View match scores
* View missing skills
* View RAG evidence
* View live job listings
* View company suggestions
* Download the analysis report

Streamlit helped me quickly create a working frontend without spending too much time on frontend complexity in the first version.

---

### 4. Supabase

Supabase is used for:

* User authentication
* Email-based login
* Basic user tracking
* Admin analytics data storage

In this project, Supabase helped me understand how authentication and user-level analytics can be added to an AI application.

---

### 5. Gemini API

Gemini API is used as the AI provider in this version.

It is used for:

* Resume and job description understanding
* Structured AI response generation
* Skill extraction
* Match analysis
* Resume suggestions
* Company suggestions
* Similar role suggestions
* Interview preparation suggestions
* Embedding generation

I switched to Gemini API to keep this beta version aligned with free-tier developer tools.

---

### 6. Embeddings and Vectors

Embeddings convert text into numerical vectors.

In this project:

```text
Resume sections → Embeddings
Job description sections → Embeddings
```

This helps the app compare meaning, not just exact keywords.

Example:

```text
"Built REST APIs"
```

and

```text
"API development experience"
```

may not use the exact same words, but they are semantically related.

---

### 7. Qdrant Cloud

Qdrant Cloud is used as the vector database.

The app stores resume chunks as vectors and retrieves the most relevant resume sections for the job description.

This helps the system provide evidence-based feedback instead of only giving a generic AI response.

---

### 8. RAG

RAG means Retrieval Augmented Generation.

In simple words:

```text
First retrieve relevant information
        ↓
Then send that context to the AI model
        ↓
Then generate a better answer
```

In this project, RAG is used to retrieve relevant resume sections before generating resume feedback.

Example:

```text
Job description asks for API development
        ↓
System retrieves resume section about REST APIs or backend work
        ↓
AI uses that evidence while giving feedback
```

---

### 9. Semantic Matching

Semantic matching helps compare meaning instead of only comparing exact words.

The app uses semantic matching to understand whether the resume experience is related to the job requirement.

This improves the quality of the match score and makes the analysis more useful.

---

### 10. Adzuna API

Adzuna API is used to fetch live job-market data.

In this project, Adzuna is used for:

* Live job listings
* Top company suggestions
* Company hiring signals
* Role/location-based job search support

If Adzuna returns live data, the app shows it in the Jobs tab.

If no live data is available, the app falls back to AI-generated strategic company suggestions.

---

### 11. PDF Report Generation

The app generates a downloadable PDF report.

The report includes:

* Match percentage
* ATS keyword score
* Semantic fit score
* Missing skills
* Resume suggestions
* Optimized headline
* Optimized summary
* Similar roles
* Company suggestions
* Final resume strategy

---

## Current Workflow Without LangGraph

Currently, the application uses a normal Python and FastAPI workflow.

The flow is controlled step by step using Python service files.

```text
main.py
  ↓
resume_parser.py
  ↓
matcher.py
  ↓
qdrant_rag_analyzer.py
  ↓
ai_suggestions.py
  ↓
adzuna_service.py
  ↓
resume_optimizer.py
  ↓
report_generator.py
```

This is a sequential workflow.

LangGraph is planned as a future upgrade to convert this into a graph-based AI workflow.

---

## Future LangGraph Plan

In the future, I plan to convert the current flow into LangGraph nodes.

Planned LangGraph flow:

```text
Resume Parser Node
        ↓
Job Description Analyzer Node
        ↓
RAG Retriever Node
        ↓
Skill Gap Analyzer Node
        ↓
Adzuna Job Market Node
        ↓
Resume Optimizer Node
        ↓
Company Recommender Node
        ↓
Report Generator Node
```

This will make the project closer to an agentic AI workflow.

---

## Future MCP Plan

MCP is planned as a future upgrade.

Possible MCP tools:

* Resume file tool
* GitHub profile tool
* Job search tool
* Company research tool
* Resume version tool

---

## Privacy Note

This is a beta version.

The application currently stores only basic analytics such as:

* Email
* Target role
* Location
* Match score
* ATS score
* Semantic score
* Timestamp

Resume text is not stored permanently in the current MVP.

Users should avoid uploading highly sensitive personal information during beta testing.

---

## Mobile Usage

The app can be opened on mobile browsers.

However, for the best experience, desktop or laptop is recommended because:

* Resume upload is easier
* Long AI feedback is easier to read
* PDF report download is easier
* Admin analytics are easier to view

---

## How to Run Locally

### Backend

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run backend:

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

---

### Frontend

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Frontend runs at:

```text
http://localhost:8501
```

---

## Environment Variables

### Backend Environment Variables

Create a local file:

```text
backend/.env
```

Add:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_EMBEDDING_DIMENSION=768

QDRANT_URL=
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=resume_rag_chunks_gemini

SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=

ADZUNA_APP_ID=
ADZUNA_APP_KEY=
ADZUNA_COUNTRY=gb

ADMIN_EMAIL=
ALLOWED_TESTER_EMAILS=
```

For private beta, use:

```env
ALLOWED_TESTER_EMAILS=your_email@example.com
```

For public beta, leave it empty:

```env
ALLOWED_TESTER_EMAILS=
```

---

### Frontend Streamlit Secrets

Create a local file:

```text
frontend/.streamlit/secrets.toml
```

Add:

```toml
SUPABASE_URL = ""
SUPABASE_ANON_KEY = ""
ADMIN_EMAIL = ""

LINKEDIN_URL = ""
GITHUB_URL = ""
BACKEND_URL = ""
```

Important:

Do not commit `.env` or `secrets.toml` files to GitHub.

---

## Deployment

### Backend Deployment

The backend is deployed using Render.

Recommended Render settings:

```text
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Backend environment variables should be added in Render dashboard, not committed to GitHub.

---

### Frontend Deployment

The frontend is deployed using Streamlit Community Cloud.

Recommended Streamlit settings:

```text
Repository: GitHub repository
Branch: main
Main file path: frontend/app.py
```

Frontend secrets should be added in Streamlit Cloud secrets manager, not committed to GitHub.

---

### Authentication and Analytics

Supabase is used for user authentication and basic analytics storage.

---

### Vector Database

Qdrant Cloud is used for storing and searching resume embeddings.

Important:

The Qdrant collection used for Gemini embeddings is:

```text
resume_rag_chunks_gemini
```

This is separate from any previous OpenAI embedding collection because embedding dimensions are different.

---

## What I Learned From This Project

This project helped me gain practical exposure to building and deploying a real AI application.

I learned how different tools work together:

* Render for backend hosting
* Streamlit Community Cloud for frontend hosting
* Supabase for authentication and analytics
* Qdrant Cloud for vector database
* Gemini API for LLM and embeddings
* Adzuna API for live job-market data
* ReportLab for PDF generation
* FastAPI for backend APIs

It also helped me understand that building a real project teaches much more than only watching tutorials.

---

## Contribution

This project is open for suggestions and improvements.

If anyone wants to contribute:

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Raise a pull request

Possible contribution areas:

* UI improvements
* Better scoring logic
* LangGraph workflow
* MCP integration
* Better Adzuna job filtering
* More detailed analytics
* Resume export improvements
* Mobile UI improvements
* Testing and bug fixes

---

## Author

Built by Kavya Singuru.

LINKEDIN_URL = "https://www.linkedin.com/in/kavya-singuru"
GITHUB_URL = "https://github.com/KavyaSinguru02/ai-job-application-copilot"
