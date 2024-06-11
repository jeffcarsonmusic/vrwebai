from langchain_community.embeddings import BedrockEmbeddings
from langchain.chains import RetrievalQA
import pinecone
from langchain_aws import BedrockLLM
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import PromptTemplate
import boto3
from dotenv import load_dotenv
import os, sys
from langchain_aws import ChatBedrock

# Load environment variables from .env file
load_dotenv()

# Initialize the boto3 client for Bedrock if not already done
boto3_bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-west-2')

# Create an Amazon Titan Text Embeddings client
embeddings_client = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", region_name="us-west-2", client=boto3_bedrock)

# Get Pinecone API key from environment variables
PC_KEY = os.getenv("PC_API_KEY")

# Create an instance of PineconeClient
pc = pinecone.Pinecone(api_key=PC_KEY)
index = pc.Index('latestone')

# Setup Pinecone vector store
vector_store = PineconeVectorStore(index_name='latestone', embedding=embeddings_client, text_key='text', pinecone_api_key=PC_KEY)
retreiver = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 15},
                verbose=True
            )

""" # Verify that the vector store contains embeddings. Useful for debugging.
def check_index_contents():
    try:
        stats = index.describe_index_stats()
        print("Index statistics:", stats)
    except Exception as e:
        print(f"Error retrieving index statistics: {e}")

check_index_contents()  """

llm = ChatBedrock(
    model_id="anthropic.claude-3-opus-20240229-v1:0",
    client=boto3_bedrock,
    #model_kwargs={"top_k": 10, "temperature": 0.6, "max_tokens_to_sample": 1500},
    
)

PROMPT_TEMPLATE = """Human: You are the pastor at Dreamers church talking to a potential parishioner. Use the following pieces of context to provide a concise answer to the question at the end. Provide the answer in a conversational manner. If you don't know the answer, just say that you don't know, don't try to make up an answer. Speak as though you are answering from top of memory. Don't make mention of "the information" or "the context". Limit your response to no more than 180 characters only.

{context}

Question: {question}
Assistant:"""

PROMPT = PromptTemplate(
    template=PROMPT_TEMPLATE, input_variables=["context", "question"]
)


def generate_response(input_text, prompt, bedrock_llm):
    try:
        qa_chain = RetrievalQA.from_chain_type(
            llm=bedrock_llm,
            chain_type="stuff",
            retriever=retreiver,
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt}
        )
        result = qa_chain.invoke({"query": input_text})
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None


text = "What time is church?"
output = generate_response(text, PROMPT, llm)

if output:
    print(output['result'])
    print(len(output['result']))
else:
    print("No result returned.")
