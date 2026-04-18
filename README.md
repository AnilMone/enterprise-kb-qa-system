# Enterprise Knowledge Base Q&A System Using Amazon Bedrock Knowledge Bases

A Retrieval-Augmented Generation (RAG) question-answering application built with Streamlit, Amazon Bedrock Knowledge Bases, and Amazon S3. It allows users to ask natural language questions about enterprise documents and receive citation-backed answers.

## Project Overview

The application provides:
- A modern web UI with sidebar navigation
- Document upload to S3 for Bedrock KB ingestion
- A question search interface powered by Amazon Bedrock
- Document listing under the Documents tab
- Analytics for session question activity
- Settings history for question review and clearing

## Folder Structure

```
Enterprise Knowledge Base Q&A System Using Amazon Bedrock Knowledge Bases/
+-- app.py                  # Main Streamlit application
+-- bedrock_rag.py          # AWS Bedrock + S3 integration logic
+-- config.py               # Application configuration and constants
+-- requirements.txt        # Python dependency list
+-- .env.template           # Template for environment variables
+-- .gitignore              # Files and folders to ignore in git
+-- docs/                   # Local sample documents for the knowledge base
    +-- finance/
    +-- hr/
        +-- faq_internal.txt
    +-- it/
    +-- ops/
+-- .streamlit/             # Optional Streamlit configuration files
```

## Setup Instructions

### 1. Create a Python virtual environment

```bash
python -m venv .venv
.venv\\Scripts\\activate   # Windows
source .venv/bin/activate  # macOS / Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AWS credentials

Copy the template and fill in your AWS credentials:

```bash
copy .env.template .env   # Windows
cp .env.template .env     # macOS / Linux
```

Then update `.env` with:

```env
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=us-east-1
```

### 4. Update Bedrock settings

Open `config.py` and confirm values for:
- `AWS_REGION`
- `KNOWLEDGE_BASE_ID`
- `S3_BUCKET_NAME`
- `S3_PREFIX`
- `MODEL_ARN`

### 5. Run the application

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Application Features

- **Knowledge Bases**: Use the search page to ask questions and get citation-backed answers.
- **Documents**: View local documents found in `docs/` and files uploaded this session.
- **Analytics**: See a graph of question activity and recent queries.
- **Settings**: Review question history and clear stored session data.

## Recommended Git Workflow

### Files to push to Git

Include:
- `app.py`
- `bedrock_rag.py`
- `config.py`
- `requirements.txt`
- `.env.template`
- `README.md`
- `.gitignore`
- `docs/` folder with sample documents
- `.streamlit/` (only if it contains project-specific config)

Exclude:
- `.venv/`
- `.env`
- `*.log`
- `__pycache__/`
- `CHANGES_SUMMARY.md`
- `search_unicode.py`
- `astra_kb.log`

### Push commands

```bash
git init
git add app.py bedrock_rag.py config.py requirements.txt .env.template README.md .gitignore docs
git commit -m "Initial commit: Enterprise KB Q&A System Using Amazon Bedrock Knowledge Bases"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## Deploying to Streamlit

1. Create a new Streamlit Community Cloud app.
2. Connect your GitHub repository.
3. Set the repository branch and app folder.
4. Add the following secrets in Streamlit settings:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_DEFAULT_REGION`
5. Deploy the app.

If the app fails due to AWS auth, verify the `.env` values and recreate secrets.

## Notes

- Do not commit the `.env` file or any local secrets.
- Keep `config.py` updated with your Bedrock Knowledge Base ID and S3 bucket details.
- After uploading new documents, sync the Bedrock Knowledge Base in the AWS Console so the data is indexed.

## Troubleshooting

- `NoCredentialsError`: Ensure `.env` exists with valid AWS keys.
- `AccessDeniedException`: Confirm IAM permissions for S3 and Bedrock.
- `ResourceNotFoundException`: Verify `KNOWLEDGE_BASE_ID` in `config.py`.
- Port issues: Use `streamlit run app.py --server.port <port>` or stop other Streamlit processes.
