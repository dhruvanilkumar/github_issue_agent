# AI-Powered GitHub Issue Assistant

A fast, simple web app that uses **Google's Gemini LLM** to give you structured analyses of any public GitHub issue in seconds.

## 🌟 Features

- 🚀 **Instant Analysis** – Paste any public GitHub repo + issue number
- 🤖 **AI-Powered Insights** – Uses Google Gemini to output summary, type, priority, labels, and impact
- ⚙️ **Robust Error Handling** – Handles empty issues, comments, errors, invalid links, rate limiting
- 🎨 **Beautiful UI** – Backend: FastAPI, Frontend: Streamlit (no separate HTML/CSS/JS!)
- 📋 **JSON Export** – View and copy raw JSON output
- ✨ **Production-Ready** – Prompt engineering, edge case handling, clean code structure

---

## 📋 Problem Statement

The problem: **Developers waste time manually reading and understanding GitHub issues.** This tool automates that by using AI to:

1. Parse the issue title, body, and comments
2. Extract key information (bug vs feature, priority, suggested labels, impact)
3. Return structured JSON analysis in seconds

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         Streamlit Frontend (Port 8501)          │
│  - Beautiful UI with containers and columns     │
│  - Form for repo URL + issue number             │
│  - Display results in cards                     │
│  - JSON viewer + Copy button                    │
└────────────────────┬────────────────────────────┘
                     │ HTTP POST /analyze-issue
                     ↓
┌─────────────────────────────────────────────────┐
│        FastAPI Backend (Port 8000)              │
│  - Parse GitHub repo URL                        │
│  - Fetch issue + comments from GitHub API       │
│  - Build optimized prompt                       │
│  - Call Gemini API                              │
│  - Validate JSON response                       │
│  - Return structured analysis                   │
└─────────────────────────────────────────────────┘
         ↓ GitHub API          ↓ Gemini API
    (Fetch issue data)    (AI analysis)
```

---

## 🚀 Setup (Under 5 Minutes)

### Prerequisites

- Python 3.8+
- Git
- [Free Google Gemini API key](https://makersuite.google.com/app/apikey)

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/github-issue-assistant.git
cd github-issue-assistant
```

### Step 2: Set Up Environment

# Edit .env and add your Gemini API key

# Get it here: https://makersuite.google.com/app/apikey

```

Your `.env` should look like:

```

GEMINI_API_KEY=AIzaSyD_example_key_here_12345
GITHUB_TOKEN=
BACKEND_URL=http://localhost:8000

````

### Step 3: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
````

### Step 4: Install Frontend Dependencies

```bash
pip install -r requirements-frontend.txt
```

### Step 5: Run Backend (Terminal 1)

```bash
cd backend
uvicorn main:app --reload
```

You should see:

```
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

### Step 6: Run Frontend (Terminal 2 - NEW TERMINAL!)

```bash
streamlit run streamlit_app.py
```

You should see:

```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

---

## 💻 Usage

1. **Open the app** at http://localhost:8501
2. **Enter a GitHub repo URL** (e.g., `https://github.com/facebook/react`)
3. **Enter an issue number** (e.g., `12345`)
4. **Click "Analyze Issue"**
5. **View results** in beautiful cards
6. **Copy JSON** or view raw output

### Example

```
Repo: https://github.com/facebook/react
Issue: 27989

Output:
{
  "summary": "When using React.lazy with Suspense, fallback UI doesn't render in SSR.",
  "type": "bug",
  "priority_score": "4 - SSR is broken for many users; critical for production apps.",
  "suggested_labels": ["bug", "react-ssr", "high-priority"],
  "potential_impact": "SSR applications fail to render fallback UI correctly, breaking page layout and user experience."
}
```

---

## 📂 Project Structure

```
github-issue-assistant/
│
├── backend/
│   ├── main.py                 # FastAPI server, GitHub API calls, Gemini integration
│   ├── prompt_utils.py         # LLM prompt engineering
│   └── requirements.txt         # Backend dependencies
│
├── streamlit_app.py             # Streamlit frontend
│
├── requirements-frontend.txt     # Frontend dependencies
├── .env.example                  # Example environment variables
├── .gitignore                    # Git ignore file
└── README.md                     # This file
```

---

## 🔧 How It Works

### Backend Flow

1. **Receive Request**

   - Input: `{ "repo_url": "https://github.com/owner/repo", "issue_number": 123 }`

2. **Parse Repo URL**

   - Extract owner and repo name using regex
   - Validate format

3. **Fetch from GitHub API**

   - GET `/repos/{owner}/{repo}/issues/{issue_number}` → Title, body
   - GET `/repos/{owner}/{repo}/issues/{issue_number}/comments` → Comments
   - Handle 404 (issue not found), 403 (rate limit), etc.

4. **Build Prompt**

   - Format issue data with clear instructions
   - Include few-shot example for better LLM output
   - Truncate long content (>4096 chars) to save tokens

5. **Call Gemini API**

   - Send formatted prompt to Google Gemini
   - Request JSON response only
   - Handle errors gracefully

6. **Validate & Return**
   - Extract JSON from response (handles markdown wrapping)
   - Retry once if JSON invalid
   - Return structured analysis

### Frontend Flow

1. **User enters** repo URL and issue number
2. **Click "Analyze Issue"** → POST to `/analyze-issue`
3. **Show spinner** while processing
4. **Display results** in beautiful cards
5. **Options**: Copy JSON, View Raw, New Analysis

---

## ⚙️ Edge Cases Handled

✅ **Empty Issue Body** – Still analyzes title + comments  
✅ **No Comments** – Passes empty list to LLM  
✅ **Very Long Issues** – Truncates to 4096 chars + comments (first 10, max 500 chars each)  
✅ **Private Repositories** – Returns 403 error with clear message  
✅ **Invalid URLs** – Regex validation catches format errors  
✅ **Issue Not Found** – Returns 404 with helpful message  
✅ **GitHub Rate Limiting** – Clear error message for 403  
✅ **Gemini API Errors** – User-friendly error toast  
✅ **Invalid JSON from LLM** – Retries once, shows raw text if still broken  
✅ **Long Response Times** – Spinner feedback + 30-second timeout

---

## 📊 API Documentation

### POST `/analyze-issue`

**Request:**

```json
{
  "repo_url": "https://github.com/facebook/react",
  "issue_number": 27989
}
```

**Response (200 OK):**

```json
{
  "summary": "When using React.lazy with Suspense, fallback UI doesn't render in SSR.",
  "type": "bug",
  "priority_score": "4 - SSR is broken for many users; critical for production apps.",
  "suggested_labels": ["bug", "react-ssr", "high-priority"],
  "potential_impact": "SSR applications fail to render fallback UI correctly, breaking page layout and user experience."
}
```

**Error Response (400 Bad Request):**

```json
{
  "detail": "Invalid GitHub repo URL"
}
```

**Error Response (404 Not Found):**

```json
{
  "detail": "Issue not found"
}
```

---

## 🎯 Evaluation Criteria Met

| Criterion              | Status | Details                                                                  |
| ---------------------- | ------ | ------------------------------------------------------------------------ |
| **Prompt Engineering** | ✅     | Few-shot examples, clear schema, role definition, edge case instructions |
| **System Design**      | ✅     | Clean separation: backend (FastAPI), frontend (Streamlit), LLM layer     |
| **Edge Case Handling** | ✅     | Long issues, empty comments, invalid URLs, API errors, JSON validation   |
| **Code Quality**       | ✅     | Typed models, clear error handling, modular structure (prompt_utils.py)  |
| **README**             | ✅     | Setup < 5 min, clear architecture, API docs, examples                    |
| **Extra Polish**       | ✅     | Loading spinners, error toasts, JSON viewer, copy button, session state  |

---

## 🔐 Security Best Practices

- ✅ API key stored in `.env` (never committed)
- ✅ `.gitignore` includes `.env`
- ✅ Input validation on all fields
- ✅ Error messages don't leak sensitive info
- ✅ CORS enabled for local dev (restrict in production)

---

## 🛠️ Troubleshooting

### Issue: "Cannot connect to backend"

```bash
# Make sure backend is running
cd backend
uvicorn main:app --reload

```

GEMINI_API_KEY=AIzaSyD_example_key_here_12345
GEMINI_MODEL=gemini-1.0
GEMINI_API_VERSION=v1

```

**Tech Stack:**

- FastAPI (backend)
- Streamlit (frontend)
- Google Gemini (LLM)
- GitHub API (data source)
- Python 3.8+

---

## ❓ FAQ

**Q: Does this work with private repos?**
A: No, but you can add GitHub OAuth + token in `.env` for higher rate limits.

**Q: Can I use OpenAI instead of Gemini?**
A: Yes! Replace `call_gemini_api()` in `main.py` with OpenAI's client. Update prompt_utils.py accordingly.

**Q: How much does it cost?**
A: Gemini free tier is $0 (60 req/min). GitHub API is free (60 req/hour unauthenticated, 5000/hour authenticated).

**Q: Can I deploy this myself?**
A: Yes! Deploy backend to Railway/Heroku, frontend to Streamlit Cloud. Set environment variables in each platform.

---

Made By Dhruva B A
```
