import os
import re
import json
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from prompt_utils import build_prompt
from typing import Optional

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_API_VERSION = os.getenv("GEMINI_API_VERSION", "v1beta")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/{GEMINI_API_VERSION}/models/{GEMINI_MODEL}:generateContent"

print(f"✅ Using Gemini Model: {GEMINI_MODEL}")
print(f"✅ API Version: {GEMINI_API_VERSION}")
print(f"✅ API URL: {GEMINI_API_URL}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    repo_url: str
    issue_number: int

def extract_owner_repo(url):
    m = re.match(
        r'https?://github\.com/([^/]+)/([^/]+)', url.strip().lower())
    if not m:
        raise ValueError("Invalid repo URL, must be in format https://github.com/owner/repo")
    return m.group(1), m.group(2)

async def fetch_github_issue(owner, repo, issue_number):
    headers = {"Accept": "application/vnd.github+json"}
    issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    async with httpx.AsyncClient() as client:
        r_issue = await client.get(issue_url, headers=headers)
        if r_issue.status_code == 404:
            raise HTTPException(status_code=404, detail="Issue not found")
        elif r_issue.status_code == 403:
            raise HTTPException(status_code=403, detail="GitHub access forbidden (possibly rate limited)")
        r_issue.raise_for_status()
        issue = r_issue.json()
        r_comments = await client.get(comments_url, headers=headers)
        comments = r_comments.json() if r_comments.status_code == 200 else []
    return {
        "title": issue.get("title", ""),
        "body": issue.get("body", ""),
        "comments": [c.get("body", "") for c in comments]
    }

async def call_gemini_api(messages):
    params = {
        "contents": [
            {"parts": [{"text": m["text"]}], "role": m.get("role", "user")}
            for m in messages
        ],
        "generationConfig": {
            "temperature": 0.4, "maxOutputTokens": 512
        }
    }
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    async with httpx.AsyncClient(timeout=25) as client:
        resp = await client.post(url, json=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Gemini API error: " + resp.text)
        gem = resp.json()
        candidates = gem.get("candidates", [])
        if not candidates or "content" not in candidates[0]:
            raise HTTPException(status_code=500, detail="No response from Gemini API")
        result = candidates[0]["content"]["parts"][0]["text"]
        return result

@app.post("/analyze-issue")
async def analyze_issue(request: AnalyzeRequest):
    try:
        owner, repo = extract_owner_repo(request.repo_url)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid GitHub repo URL")
    try:
        issue_data = await fetch_github_issue(owner, repo, request.issue_number)
    except HTTPException as e:
        raise e
    prompt = build_prompt(issue_data)
    messages = [{"role": "user", "text": prompt}]
    response = await call_gemini_api(messages)
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    try:
        json_out = json.loads(json_match.group(0)) if json_match else json.loads(response)
    except Exception:
        fix_prompt = (
            "The following text is not valid JSON, fix it so it *only* contains valid JSON:\n"
            + response
        )
        messages.append({"role": "user", "text": fix_prompt})
        fixed = await call_gemini_api(messages)
        try:
            json_out = json.loads(re.search(r'\{.*\}', fixed, re.DOTALL).group(0))
        except Exception:
            raise HTTPException(status_code=500, detail="LLM output invalid JSON. Try again.")
    return json_out