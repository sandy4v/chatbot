import boto3
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import BedrockEmbeddings  # Use Bedrock embeddings
from langchain_community.vectorstores import FAISS  # Or Chroma, as you prefer
# from langchain.vectorstores import Chroma

# AWS S3 Configuration
bucket_name = "sandeep-patharkar-gen-ai-bckt"  # Replace with your bucket name

# Vectorstore Path
persist_directory = 'db'  # Directory to store the Chroma vectorstore

def load_all_pdfs_from_s3(bucket_name):
    """Loads all PDF documents from an S3 bucket using PyPDFLoader."""
    documents = []
    try:
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=bucket_name)

        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                if key.lower().endswith(".pdf"):
                    print(f"Loading PDF: {key}")
                    try:
                        pdf_object = s3.get_object(Bucket=bucket_name, Key=key)
                        pdf_file = pdf_object['Body'].read()
                        temp_file_path = "temp.pdf"
                        with open(temp_file_path, "wb") as f:
                            f.write(pdf_file)
                        loader = PyPDFLoader(temp_file_path)
                        loaded_documents = loader.load()
                        documents.extend(loaded_documents)
                        os.remove(temp_file_path)
                    except Exception as e:
                        print(f"Error loading PDF {key}: {e}")
        else:
            print(f"No objects found in bucket {bucket_name}")

    except Exception as e:
        print(f"Error listing objects in S3 bucket: {e}")
        return []

    return documents

def create_chunks(documents, chunk_size=1000, chunk_overlap=100):
    """Splits the documents into smaller chunks for processing."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def create_vector_store(chunks, embeddings, persist_directory="faiss_index"): #changed persist_directory name to "faiss_index"
    """Creates a FAISS vector store from the document chunks.""" #changed to FAISS
    vectordb = FAISS.from_documents(chunks, embeddings)
    vectordb.save_local(persist_directory)
    return vectordb

# Main execution
if __name__ == "__main__":
    # 1. Load PDFs from S3
    documents = load_all_pdfs_from_s3(bucket_name)

    if not documents:
        print("No documents loaded.  Exiting.")
        exit()

    # 2. Create Chunks
    chunks = create_chunks(documents)
    print(f"Created {len(chunks)} chunks")

    # 3. Create Bedrock Embeddings
    print("Creating Bedrock embeddings...")
    bedrock_embeddings = BedrockEmbeddings(credentials_profile_name="default", model_id="amazon.titan-embed-text-v1")
    print("Bedrock embeddings created.")

    # 4. Create Vectorstore
    # embeddings = OpenAIEmbeddings()  # Initialize OpenAI embeddings #commented out since we are using bedrock
    vectordb = create_vector_store(chunks, bedrock_embeddings, persist_directory) #added persist directory
    print(f"FAISS vector store created and persisted to {persist_directory}") #changed to FAISS