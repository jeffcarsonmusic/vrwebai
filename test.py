import os
import logging
import json
import boto3
import jsonlines
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_community.embeddings import BedrockEmbeddings

# Load environment variables
load_dotenv()

# Constants
MODEL_ID = "amazon.titan-embed-text-v2:0"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")
CLOUD = 'aws'
REGION = 'us-east-1'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Bedrock and Pinecone clients
boto3_bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-west-2')
embeddings_client = BedrockEmbeddings(model_id=MODEL_ID)
spec = ServerlessSpec(cloud=CLOUD, region=REGION)
pinecone = Pinecone(api_key=PINECONE_API_KEY)

# Load data from jsonlines file
def load_data(file_path):
    with jsonlines.open(file_path) as reader:
        return [item for item in reader]

# Initialize Pinecone index
def init_pinecone(index, dimension):
    if index not in pinecone.list_indexes().names():
        pinecone.create_index(name=index, dimension=dimension, metric="euclidean", spec=spec)
    return pinecone.Index(index)

# Create and index embeddings
def create_and_index_embeddings(data, pinecone_index):
    for item in data:
        text = item["text"]
        doc_id = f"{item['source'].split('/')[-1]}"
        embedding = embeddings_client.embed_query(text)
        
        vector = {
            "id": doc_id,
            "values": embedding,
            "metadata": {"source": item["source"], "text": text}
        }
        
        pinecone_index.upsert(vectors=[vector])
        logging.info(f"Indexed: {doc_id}")

# Get embeddings dimension
def get_embedding_dimension():
    response = boto3_bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({"inputText":"sample_text"}),
        contentType="application/json",
        accept="application/json"
    )
    response_body = json.loads(response['body'].read())
    return len(response_body['embedding'])

# Main execution
if __name__ == "__main__":
    train_data = load_data("./train.jsonl")
    embedding_dimension = get_embedding_dimension()
    pinecone_index = init_pinecone(INDEX_NAME, embedding_dimension)
    create_and_index_embeddings(train_data, pinecone_index)
