from langchain_aws import BedrockLLM  # New import from langchain-aws
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import streamlit as st
import boto3
import os

# Setup AWS and model ID for Bedrock
bedrock_client = BedrockLLM(model_id="amazon.titan-embed-text-v1")

# Create a prompt template
prompt = PromptTemplate(input_variables=["query"], template="Answer the following question: {query}")

# Setup the chain
llm_chain = LLMChain(llm=bedrock_client, prompt=prompt)

# Streamlit setup
st.title("Chatbot for AWS Cost Optimization")
user_input = st.text_input("Enter your query:")

if user_input:
    response = llm_chain.run(query=user_input)
    st.write(response)