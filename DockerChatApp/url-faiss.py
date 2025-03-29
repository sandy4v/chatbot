import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
import os
import boto3
from langchain.embeddings import BedrockEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import Bedrock  # Import Bedrock integration

# 1. Load the PDF
print("Loading PDF...")
loader = PyPDFLoader("https://www.regeneron.com/downloads/regeneron-position-ethics-clinical-studies.pdf")  # Replace with your PDF URL
documents = loader.load()
print(f"PDF loaded. Number of documents: {len(documents)}")

# 2. Split into chunks
print("Splitting into chunks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)
print(f"Split into {len(chunks)} chunks")

# 3. Create Bedrock embeddings
print("Creating Bedrock embeddings...")
bedrock_embeddings = BedrockEmbeddings(credentials_profile_name="default", model_id="amazon.titan-embed-text-v1")
print("Bedrock embeddings created.")

# 4. Create FAISS vector store
print("Creating FAISS vector store...")
db = FAISS.from_documents(chunks, bedrock_embeddings)
print("FAISS vector store created.")

# 5. (Optional) Save the vector store locally
print("Saving FAISS vector store locally...")
db.save_local("faiss_index")
print("FAISS vector store saved locally.")

# Streamlit UI
st.title("Regeneron Ethics QA")  # Add a title to the app

query = st.text_input("Enter your question about Regeneron's ethics policy:")  # Add a text input field

if query:  # If the user has entered a question
    st.write("You asked:", query)  # Display the question

    # 6.  Create the Bedrock LLM
    bedrock_llm = Bedrock(model_id="anthropic.claude-v2", credentials_profile_name="default")  # Replace with your Bedrock model ID

    # 7. Create the RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(llm=bedrock_llm,chain_type="stuff",retriever=db.as_retriever(search_kwargs={'k': 3})) # Adjust k as needed

    # 8. Run the query and display the result
    answer = qa_chain.run(query)
    st.write("Answer:", answer)