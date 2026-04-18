# ============================================================
# FILE: config.py
# PURPOSE: Stores ALL settings/constants in one central place.
#          If you need to change something (like region or model),
#          you only change it HERE - not in 5 different files.
# ============================================================

# --- AWS Region ---
# This is the AWS data center region where your services live.
# us-east-1 = North Virginia (most services available here)
AWS_REGION = "us-east-1"

# --- AWS Account ID ---
AWS_ACCOUNT_ID = "211125429674"

# --- S3 Bucket Name ---
# S3 = Simple Storage Service (AWS cloud file storage)
# This bucket holds your company documents (PDFs, text files, etc.)
S3_BUCKET_NAME = "enterprise-bedrock-rag-private-data"

# --- S3 Folder (Prefix) ---
# Inside your S3 bucket, documents will be stored in this folder.
# Think of it like a folder path: my-bucket/documents/file.pdf
S3_PREFIX = "documents/"

# --- Bedrock Knowledge Base ID ---
# After you create a Knowledge Base in AWS Bedrock console,
# it gives you a unique ID (like "ABCD1234EF").
# Paste that ID here.
KNOWLEDGE_BASE_ID = "XX74MIAIHH"

# --- Embedding Model ---
# The model used to convert text into vectors for the Knowledge Base.
EMBEDDING_MODEL = "amazon.titan-embed-text-v1"

# --- Foundation Model ARN ---
# ARN = Amazon Resource Name (unique identifier for any AWS resource).
# This specifies WHICH AI model generates the final answer.
#
# NOTE: Anthropic Claude models require an active AWS Marketplace
# subscription with a valid payment method. Use Amazon Nova models
# for standard Bedrock access with no marketplace payment required.
#
# Amazon Nova Pro  - powerful, multi-modal, no marketplace subscription
# Amazon Nova Lite - fast & cost-effective, no marketplace subscription
MODEL_ARN = (
    "arn:aws:bedrock:us-east-1::foundation-model/"
    "amazon.nova-pro-v1:0"
)

# --- How many document chunks to retrieve ---
# When you ask a question, Bedrock searches your docs and finds
# the top N most relevant text chunks to give the AI as context.
MAX_CHUNKS = 5
NUMBER_OF_RESULTS = MAX_CHUNKS

# --- Logging configuration ---
ENABLE_LOGGING = True
LOG_FILE = "astra_kb.log"
LOG_LEVEL = "INFO"

# --- App display settings ---
APP_TITLE = "Enterprise Knowledge Base Q&A System Using Amazon Bedrock Knowledge Bases"
APP_ICON = "K"    # plain text label for browser tab