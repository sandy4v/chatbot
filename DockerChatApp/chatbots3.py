import boto3  # Import the boto3 library for interacting with AWS services
import os  # Import the os library for interacting with the operating system
from langchain_community.document_loaders import PyPDFLoader  # Import PyPDFLoader to load PDF documents
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Import RecursiveCharacterTextSplitter to split text into chunks
from langchain_community.embeddings import BedrockEmbeddings  # Import BedrockEmbeddings to create embeddings using AWS Bedrock
from langchain_community.vectorstores import FAISS  # Import FAISS for creating a vector store
from PyPDF2 import PdfReader # Import PdfReader from PyPDF2

from langchain.docstore.document import Document # Import Document

# AWS S3 Configuration
bucket_name = "sandeep-patharkar-gen-ai-bckt"  # Replace with your bucket name

# Vectorstore Path
persist_directory = 'db'  # Directory to store the FAISS vectorstore

def load_all_pdfs_from_s3(bucket_name):

    #Loads all PDF documents from an S3 bucket, handling potential loading errors.

    documents = []  # Initialize an empty list to store the loaded documents
    try:
        s3 = boto3.client('s3')  # Create an S3 client object
        response = s3.list_objects_v2(Bucket=bucket_name)  # List all objects in the bucket

        if 'Contents' in response:  # Check if the bucket contains any objects
            for obj in response['Contents']:  # Iterate over each object in the bucket
                key = obj['Key']  # Get the object's key (filename)
                if key.lower().endswith(".pdf"):  # Check if the object is a PDF file
                    print(f"Loading PDF: {key}")  # Print a message indicating which PDF is being loaded
                    temp_file_path = "/tmp/temp.pdf"  # Define the path for the temporary file

                    try:
                        # 1. Download PDF to a temporary file
                        s3.download_file(bucket_name, key, temp_file_path)  # Download the PDF from S3 to the temp file

                        # 2. Try loading with PyPDF2
                        text = ""  # Initialize an empty string to store the extracted text
                        with open(temp_file_path, 'rb') as f:  # Open the temp file in binary read mode
                            reader = PdfReader(f)  # Create a PdfReader object
                            for page in reader.pages:  # Iterate over each page in the PDF
                                text += page.extract_text() or ""  # Extract the text from the page and append it to the string

                        documents.append(Document(page_content=text, metadata={"source": key}))  # Create a Document object and add it to the list
                        print(f"Successfully loaded PDF with PyPDF2: {key}")  # Print a success message

                    except Exception as e_pypdf2:
                        print(f"PyPDF2 failed for {key}: {e_pypdf2}.  Falling back to PyPDFLoader.")  # Print an error message and indicate fallback
                        try:
                            # 3. Fallback to PyPDFLoader
                            loader = PyPDFLoader(temp_file_path)  # Create a PyPDFLoader object
                            loaded_documents = loader.load()  # Load the PDF using PyPDFLoader
                            documents.extend(loaded_documents)  # Add the loaded documents to the list
                            print(f"Successfully loaded PDF with PyPDFLoader: {key}")  # Print a success message

                        except Exception as e_loader:
                            print(f"PyPDFLoader also failed for {key}: {e_loader}")  # Print an error message if PyPDFLoader also fails

                    finally:
                        # 4. Clean up the temporary file
                        try:
                            os.remove(temp_file_path)  # Delete the temporary file
                        except OSError as e:
                            print(f"Error deleting temporary file {temp_file_path}: {e}")  # Print an error message if deletion fails

        else:
            print(f"No objects found in bucket {bucket_name}")  # Print a message if the bucket is empty

    except Exception as e:
        print(f"Error listing objects in S3 bucket: {e}")  # Print an error message if listing objects fails
        return []  # Return an empty list if an error occurs

    return documents  # Return the list of loaded documents

def create_chunks(documents, chunk_size=1000, chunk_overlap=100):
    """Splits the documents into smaller chunks for processing."""
    text_splitter = RecursiveCharacterTextSplitter(  # Create a RecursiveCharacterTextSplitter instance
        chunk_size=chunk_size, chunk_overlap=chunk_overlap  # Set the chunk size and overlap
    )
    chunks = text_splitter.split_documents(documents)  # Split the documents into chunks
    return chunks  # Return the list of chunks

def create_vector_store(chunks, embeddings, persist_directory="faiss_index"):
    """Creates a FAISS vector store from the document chunks."""
    try:
        vectordb = FAISS.from_documents(chunks, embeddings)  # Create a FAISS vector store from the chunks and embeddings
        vectordb.save_local(persist_directory)  # Save the FAISS vector store to the specified directory
        print(f"FAISS vector store created and persisted to {persist_directory}")  # Print a success message
        return vectordb  # Return the created vector store
    except Exception as e:
        print(f"Error creating or saving FAISS vector store: {e}")  # Print an error message if creation or saving fails
        return None  # Return None if an error occurs

# Main execution
if __name__ == "__main__":
    # 1. Load PDFs from S3
    documents = load_all_pdfs_from_s3(bucket_name)  # Load all PDF documents from the S3 bucket

    if not documents:  # Check if any documents were loaded
        print("No documents loaded.  Exiting.")  # Print a message and exit if no documents were loaded
        exit()  # Exit the program

    # 2. Create Chunks
    chunks = create_chunks(documents)  # Split the loaded documents into chunks
    print(f"Created {len(chunks)} chunks")  # Print the number of chunks created

    # 3. Create Bedrock Embeddings
    print("Creating Bedrock embeddings...")  # Print a message indicating that Bedrock embeddings are being created
    try:
        bedrock_embeddings = BedrockEmbeddings(credentials_profile_name="default", model_id="amazon.titan-embed-text-v1")  # Create Bedrock embeddings
        print("Bedrock embeddings created.")  # Print a success message
    except Exception as e:
        print(f"Error creating Bedrock embeddings: {e}")  # Print an error message if embedding creation fails
        bedrock_embeddings = None  # Set embeddings to None to prevent further errors

    # 4. Create Vectorstore
    if bedrock_embeddings:  # Only create the vector store if embeddings were successfully created
        vectordb = create_vector_store(chunks, bedrock_embeddings, persist_directory)  # Create the FAISS vector store
        if vectordb: # Check if the vector store was created successfully
            print(f"FAISS vector store created and persisted to {persist_directory}")  # Print a success message
        else:
            print("Failed to create FAISS vector store.")  # Print a failure message
    else:
        print("Bedrock embeddings were not created, skipping vector store creation.")  # Print a message if embeddings were not created