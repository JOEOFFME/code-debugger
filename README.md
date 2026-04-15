# Debugger — AI Python Assistant

An AI-powered Python code debugger that classifies bugs, explains them, and generates fixes automatically.

## Features

- **Bug Classification** — Identifies Syntax Errors, Runtime Errors, Logic Bugs, and Multiple Issues using CodeBERT
- **AI Explanation** — Groq-powered natural language explanation of what went wrong
- **Auto Fix** — Generates corrected code with a unified diff
- **Semantic Search** — Finds similar bugs from a session-level index using embeddings
- **Attention Heatmap** — Visualizes which tokens the model focuses on

## Project Structure

```
debugger/
├── app.py              # Flask app + API routes + ML inference
├── groq_fixer.py       # Groq LLM integration for fixes & diffs
├── templates/
│   └── index.html      # Frontend (single-file, no framework)
├── requirements.txt
├── Procfile            # Railway / Heroku
├── Dockerfile          # Docker / HF Spaces
├── .env.example
└── ci.yml              # GitHub Actions CI
```

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/code-debugger.git
cd code-debugger

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Run
python app.py
# Open http://localhost:8080
```

## Deploy to Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Select your repo
4. Go to **Variables** tab → add `GROQ_API_KEY=your_key_here`
5. Railway auto-detects the `Procfile` and deploys — done ✅

> Railway injects `$PORT` automatically. The app reads it via `os.environ.get("PORT", 8080)`.

## Deploy via Docker

```bash
docker build -t debugger .
docker run -p 8080:8080 -e GROQ_API_KEY=your_key debugger
```
