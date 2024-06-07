import jsonlines
import os
import boto3
import logging
from pinecone import ServerlessSpec
logging.basicConfig(level=logging.INFO)
from dotenv import load_dotenv
from langchain_community.embeddings import BedrockEmbeddings
import json
from pinecone import Pinecone

# Load environment variables from .env file
load_dotenv()

MODEL_ID = "amazon.titan-embed-text-v2:0"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")
cloud = 'aws'
region = 'us-east-1'

spec = ServerlessSpec(cloud=cloud, region=region)
# Initialize the boto3 client for Bedrock if not already done
boto3_bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-west-2')

# Create an Amazon Titan Text Embeddings client
embeddings_client = BedrockEmbeddings(model_id=MODEL_ID)

# Load train.jsonl file
def load_data(file_path):
    data = []
    with jsonlines.open(file_path) as f:
        for item in f:
            data.append(item)
    return data

# Initialize Pinecone index
def init_pinecone(pc_api_key, index, dimension):

    pc = Pinecone(api_key=pc_api_key)

    if index not in pc.list_indexes().names():
        pc.create_index(
            name = index,
            dimension = dimension,
            metric = "euclidean", # or "cosine" or other supported metrics
            spec=spec
        )
    return pc.Index(index)

# Create embeddings and populate the index
def create_and_index_embeddings(data, pinecone, index):
    batch_size = 1
    vectors = []
    for start_index in range(0, len(data), batch_size):
        # Parse for text key
        text_batch = [item["text"] for item in data[start_index:start_index+batch_size]]
        # Correct the references for ids_batch based on the new structure
        ids_batch = [
            f"{item['source'].split('/')[-1]}_{i}"  # Use 'source' to generate the identifier
            for i, item in enumerate(data[start_index:start_index+batch_size])
        ]
        print(ids_batch)

        embedding = embeddings_client.embed_documents(text_batch)
        # Assuming embedding is the result from embeddings_client.embed_documents(text_batch)
        #flattened_embedding = [item for sublist in embedding for item in sublist]
        logging.info(f"Batch {start_index} embeddings generated.")
        print("embedding", embedding)
        
                # Flatten the embedding if it is a list of lists
        if isinstance(embedding[0], list):
            embedding = [item for sublist in embedding for item in sublist]

        # Ensure all elements are floats
        if isinstance(embedding, list) and all(isinstance(x, float) for x in embedding):
            vectors.append({
                "id": str(ids_batch),
                "values": embedding,
                "metadata": {
                    "source": data[start_index]["source"],
                    "text": str(text_batch),
                }
            })
        else:
            raise ValueError(f"Invalid embedding for document {i}: {embedding}")
 
        # Update 'to_upsert' with the correct metadata structure
        to_upsert = [
            {
                "id": str(ids_batch),
                "values": embedding,
                "metadata": {
                    "source": data[start_index]["source"],
                    "text": str(text_batch)
                }
            }
        ]
        for i in range(len(ids_batch)):
            pinecone.upsert(vectors=to_upsert)


    logging.info("Embeddings indexed successfully.")

# Get embeddings dimension from Amazon Bedrock Titan
def get_embedding_dimension():

    #try:
    response = boto3_bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({"inputText":"sample_text"}),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response['body'].read())
    sample_embedding = response_body['embedding']
    return len(sample_embedding)

# Load the data from train.jsonl
train_data = load_data("./train.jsonl")

# Get embeddings dimension from Amazon Bedrock Titan
EMBEDDING_DIMENSION = get_embedding_dimension()

# Initialize Pinecone index
pc = init_pinecone(PINECONE_API_KEY, INDEX_NAME, EMBEDDING_DIMENSION )

# Create embeddings and populate the index with the train data
create_and_index_embeddings(train_data, pc, INDEX_NAME)