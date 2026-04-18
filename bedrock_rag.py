# ============================================================
# FILE: bedrock_rag.py
# PURPOSE: This file contains ALL the logic for:
#   1. Connecting to Amazon Bedrock
#   2. Sending a question to the Knowledge Base
#   3. Retrieving relevant document chunks (the "R" in RAG)
#   4. Getting the AI to generate a cited answer (the "G" in RAG)
#   5. Uploading documents to S3
#   6. Returning the answer + citations back to the Streamlit UI
# ============================================================


# ============================================================
# SECTION 1: IMPORTS
# ============================================================

import os

import logging

import boto3

from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
# ClientError = the specific error boto3 raises when AWS rejects a request
# NoCredentialsError = AWS credentials are not configured

from dotenv import load_dotenv

from config import (
    AWS_REGION,
    KNOWLEDGE_BASE_ID,
    MODEL_ARN,
    NUMBER_OF_RESULTS,
    S3_BUCKET_NAME,
    S3_PREFIX,
    ENABLE_LOGGING,
    LOG_FILE,
    LOG_LEVEL,
)


# ============================================================
# SECTION 2: INITIALIZATION
# Runs once when this file is imported by app.py
# ============================================================

# Load .env file so AWS credentials are available to boto3.
# Using an explicit path so credentials are always found regardless
# of which directory the app is launched from.
import pathlib
_ENV_PATH = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=True)

# Set up the logger for this file.
log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
if ENABLE_LOGGING:
    logging.basicConfig(
        filename=LOG_FILE,
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
else:
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

# Create a logger specifically named "bedrock_rag".
# Terminal messages will look like: INFO:bedrock_rag:your message here
logger = logging.getLogger(__name__)
# __name__ automatically becomes "bedrock_rag" (the filename without .py)


# ============================================================
# FUNCTION 1: get_bedrock_client()
# Creates a connection to Amazon Bedrock Agent Runtime
# ============================================================

def get_bedrock_client():
    """
    Creates and returns a boto3 client for Amazon Bedrock Agent Runtime.

    WHY "bedrock-agent-runtime"?
    ----------------------------
    AWS Bedrock has two separate services:
      "bedrock"               -> for listing/configuring models (not needed here)
      "bedrock-agent-runtime" -> for RUNNING queries using Knowledge Bases

    HOW AUTHENTICATION WORKS:
    --------------------------
    boto3 automatically looks for credentials in this order:
      1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
         <- load_dotenv() above loads these from your .env file
      2. ~/.aws/credentials file (if you ran "aws configure")
      3. IAM Role attached to EC2 (used when deployed on AWS)

    Returns:
        boto3 client object ready to make Bedrock API calls
    """
    try:
        client = boto3.client(
            service_name="bedrock-agent-runtime",
            region_name=AWS_REGION,
        )
        logger.info("Bedrock client created successfully")
        return client

    except Exception as e:
        logger.error(f"Failed to create Bedrock client: {e}")
        raise  # re-throw so the caller knows it failed


# ============================================================
# FUNCTION 2: query_knowledge_base()
# The MAIN function -- takes a question, returns an AI answer
# ============================================================

def query_knowledge_base(question: str) -> dict:
    """
    Core RAG function. Steps:
      1. Takes the user's question as plain text
      2. Sends it to Amazon Bedrock Knowledge Base
      3. Bedrock converts the question into a vector (embedding)
      4. Bedrock searches the vector database for similar document chunks
      5. The matching chunks are sent to the AI model as context
      6. The model generates a grounded answer based ONLY on your documents
      7. We extract the answer + citations and return them

    Args:
        question (str): User's natural language question
                        e.g. "What is the leave policy for new employees?"

    Returns:
        dict: {
            "success":   True or False,
            "answer":    "According to the HR handbook...",
            "citations": [
                {"source": "s3://bucket/docs/file.pdf", "excerpt": "..."},
                ...
            ]
        }
    """

    # Step 1: Get the Bedrock connection
    client = get_bedrock_client()

    try:
        logger.info(f"Querying Knowledge Base '{KNOWLEDGE_BASE_ID}' with: {question}")

        # Step 2: Call retrieve_and_generate()
        # --------------------------
        # This single API call does BOTH:
        #   RETRIEVE -> searches your vector DB for relevant document chunks
        #   GENERATE -> sends those chunks + question to the model for an answer
        #
        # retrievalConfiguration sets how many chunks (NUMBER_OF_RESULTS) to retrieve.
        response = client.retrieve_and_generate(
            input={
                "text": question
            },
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "modelArn": MODEL_ARN,
                },
            },
        )

        # Step 3: Extract the generated answer text
        answer_text = response["output"]["text"]
        logger.info("Answer received from Bedrock successfully")

        # Step 4: Extract citations
        # --------------------------
        # Bedrock tells us WHICH document chunks it used to form the answer.
        # This is called "grounding" -- the answer is backed by your actual documents.
        citations = []

        for citation in response.get("citations", []):
            for reference in citation.get("retrievedReferences", []):
                # The S3 file path where the source document lives
                # Example: "s3://enterprise-bedrock-rag-private-data/documents/hr_policy.pdf"
                source_uri = reference["location"]["s3Location"]["uri"]

                # The actual text snippet from the document that was used
                excerpt = reference["content"]["text"]

                # Trim the excerpt to 400 characters for display
                excerpt_preview = (
                    excerpt[:400] + "..."
                    if len(excerpt) > 400
                    else excerpt
                )

                citations.append({
                    "source":  source_uri,
                    "excerpt": excerpt_preview,
                })

        # Step 5: Remove duplicate citations
        # (same document may appear multiple times if multiple chunks matched)
        seen_sources = set()
        unique_citations = []

        for cite in citations:
            if cite["source"] not in seen_sources:
                seen_sources.add(cite["source"])
                unique_citations.append(cite)

        logger.info(f"Returning {len(unique_citations)} unique citation(s)")

        # Step 6: Return the final result as a clean dictionary
        return {
            "success":   True,
            "answer":    answer_text,
            "citations": unique_citations,
        }

    except ClientError as e:
        # ClientError = AWS rejected the request.
        # Common causes:
        #   - Wrong Knowledge Base ID in config.py
        #   - IAM user does not have BedrockFullAccess permission
        #   - Model access not enabled in Bedrock console
        error_code    = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        logger.error(f"AWS ClientError [{error_code}]: {error_message}")

        return {
            "success":   False,
            "answer":    f"AWS Error [{error_code}]: {error_message}",
            "citations": [],
        }

    except NoCredentialsError:
        error_message = "AWS Credentials not found. Please configure your .env file with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY, or run 'aws configure'."
        logger.error(error_message)
        return {
            "success": False,
            "answer": error_message,
            "citations": [],
        }

    except Exception as e:
        # Any other unexpected Python error
        logger.error(f"Unexpected error in query_knowledge_base: {e}")

        return {
            "success":   False,
            "answer":    f"An unexpected error occurred: {str(e)}",
            "citations": [],
        }


# ============================================================
# FUNCTION 3: upload_document_to_s3()
# Uploads a file from local computer to your S3 bucket
# ============================================================

def upload_document_to_s3(file_path: str, file_name: str) -> bool:
    """
    Uploads a local file to the S3 bucket so Bedrock can index it.

    After uploading, go to the Bedrock console and click "Sync"
    so Bedrock re-reads the new file and adds it to the vector database.

    Args:
        file_path (str): Full local path to the file
                         Example: "C:/Users/You/AppData/Local/Temp/policy.pdf"
        file_name (str): What to name the file inside S3
                         Example: "policy.pdf"

    Returns:
        bool: True if upload was successful, False if it failed
    """

    # Create a separate S3 client (different service from Bedrock)
    s3_client = boto3.client("s3", region_name=AWS_REGION)

    # Build the S3 key (full path inside the bucket)
    # S3_PREFIX = "documents/" so s3_key = "documents/policy.pdf"
    s3_key = S3_PREFIX + file_name

    try:
        s3_client.upload_file(
            Filename=file_path,
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
        )
        logger.info(f"Uploaded '{file_name}' to s3://{S3_BUCKET_NAME}/{s3_key}")
        return True

    except NoCredentialsError:
        logger.error("Failed to upload: AWS Credentials not configured.")
        return False

    except ClientError as e:
        # Common causes:
        #   - IAM user does not have S3 write permission
        #   - Bucket name is wrong in config.py
        #   - File does not exist at file_path
        logger.error(f"Failed to upload '{file_name}' to S3: {e}")
        return False