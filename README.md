# Enterprise Knowledge Base Q&A System

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.23.1-red.svg)](https://streamlit.io)
[![AWS](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A **Retrieval-Augmented Generation (RAG)** powered enterprise knowledge base application that enables natural language Q&A over your organization's documents using **Amazon Bedrock Knowledge Bases** and **Amazon S3**.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [Application Pages](#application-pages)
- [Important Notes](#important-notes)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **Intelligent Q&A Search** – Ask questions in plain English and get AI-generated answers backed by your enterprise documents
- **Citation-Backed Answers** – Every response includes source references showing exactly which documents were used
- **Document Upload** – Upload PDF, TXT, and DOCX files directly from the UI to your S3 knowledge base
- **Multi-Department Support** – Organized document folders for HR, Finance, IT, and Operations
- **Session Analytics** – Track and visualize question activity with interactive charts
- **Question History** – Review and manage your past queries with a built-in history log
- **Modern Sidebar Navigation** – Clean, intuitive UI with easy navigation between sections
- **Custom Styling** – Professionally designed with a warm amber color theme using the Inter font family

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **Backend** | Python (boto3) |
| **AI/ML** | Amazon Bedrock (Nova Pro) |
| **Embeddings** | Amazon Titan Embed Text V1 |
| **Storage** | Amazon S3 |
| **Knowledge Base** | Amazon Bedrock Knowledge Bases |
| **Environment** | python-dotenv |

---

## Architecture

```
+---------------------+       +-----------------------------+
|  User (Browser)     |----->|  Streamlit Web App          |
|  localhost:8501     |       |  (app.py)                   |
+---------------------+       +--------------+--------------+
                                              |
                                              v
                               +-----------------------------+
                               |  Bedrock RAG Engine         |
                               |  (bedrock_rag.py)           |
                               +---------------+-------------+
                                               |
         +--------------------------+-----------+--------------------------+
         v                          v                                      v
+---------------------+    +---------------------+              +---------------------+
| Amazon Bedrock      |    | Amazon S3 Bucket    |              | Embedding Model     |
| Knowledge Base      |    | (Document Storage)  |              | (Titan Embed V1)    |
+---------------------+    +---------------------+              +---------------------+
```

---

## Project Structure

```
enterprise-kb-qa-system/
├── app.py              # Main Streamlit application (UI + logic)
├── bedrock_rag.py      # AWS Bedrock + S3 integration (RAG engine)
├── config.py           # Centralized configuration & constants
├── requirements.txt    # Python dependencies
├── .env.template       # Environment variable template
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── .streamlit/         # Streamlit configuration (optional)
└── docs/               # Sample enterprise documents
    ├── finance/
    │   └── travel_reimbursement.pdf
    └── hr/
        └── employee_policy.pdf
```

---

## Setup & Installation

### Prerequisites

- Python 3.7 or higher
- AWS Account with access to Amazon Bedrock
- An active **Bedrock Knowledge Base** configured in the AWS Console
- An **S3 Bucket** for document storage

### Step 1: Clone the Repository

```bash
git clone https://github.com/AnilMone/enterprise-kb-qa-system.git
cd enterprise-kb-qa-system
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure AWS Credentials

Copy the environment template:

```bash
# Windows
copy .env.template .env

# macOS / Linux
cp .env.template .env
```

Then update `.env` with your AWS credentials:

```.env
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=us-east-1
```

---

## Configuration

Open `config.py` and set the following values:

| Variable | Description |
|----------|-------------|
| `AWS_REGION` | Your AWS region (e.g., `us-east-1`) |
| `KNOWLEDGE_BASE_ID` | Bedrock Knowledge Base ID from AWS Console |
| `S3_BUCKET_NAME` | Name of your S3 bucket |
| `S3_PREFIX` | Folder path inside S3 (e.g., `documents/`) |
| `MODEL_ARN` | ARN of the foundation model to use |

> **Note:** The Amazon Nova Pro model is used by default and requires no marketplace subscription.

---

## Running the App

Start the Streamlit application:

```bash
streamlit run app.py
```

Open your browser and navigate to:

**http://localhost:8501**

---

## Application Pages

### Knowledge Bases

The main Q&A interface. Type your question, and the app retrieves relevant document chunks, sends them to Amazon Bedrock, and returns a grounded answer with citations.

### Documents

Browse all documents available in the `docs/` folder and files uploaded during the current session.

### Analytics

Visualize your question activity with a session-based line chart and review your most recent queries.

### Settings

Review your complete question history and clear session data when needed.

---

## Important Notes

- Never commit the `.env` file or any AWS secrets to version control
- After uploading new documents, **sync your Bedrock Knowledge Base** in the AWS Console to re-index the data
- Keep `config.py` updated whenever you change your Knowledge Base ID or S3 bucket

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| `NoCredentialsError` | Ensure `.env` exists with valid AWS keys |
| `AccessDeniedException` | Verify IAM permissions for S3 and Bedrock |
| `ResourceNotFoundException` | Check `KNOWLEDGE_BASE_ID` in `config.py` |
| Port already in use | Run `streamlit run app.py --server.port 8502` |

---

## License

This project is licensed under the MIT License.

---

**Built with Amazon Bedrock Knowledge Bases by AnilMone**
