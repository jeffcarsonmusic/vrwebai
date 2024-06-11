# RAG Chatbot App Components for Suggested Response

This Python repository contains a set of scripts that allow you to scrape a website, clean the data, organize it, chunk it, and then vectorize it. The resulting vectors can be used for a variety of machine learning tasks, such as similarity search or clustering.

## Folders
data_loader - Website scraping files
pdf - Used for pdf-muncher.py (WIP)
sitepages - Created by get_website.py in data_loader folder

## Files
pdf-muncher.py - WIP
rag-call.py - The file that the eventual customer app API will hit to make the RAG call to the vector DB
requirements.txt - dependencies
run_locally - Bash script to run the scraping pipeline from local


In data_loader folder
- `get_website.py`: This script downloads a website using wget, reads and cleans the HTML files using Beautiful Soup, and saves the resulting text files in a specified directory.
- `chunk_data.py`: This script splits the text files into smaller chunks, using a recursive character-based text splitter. The resulting chunks are saved in a JSONL file.
- `vectorize_upsert.py`: This script loads the JSONL file, creates embeddings using Amazon Titan's amazon.titan-embed-text-v2:0 model, and indexes the embeddings using Pinecone. This is the one script you need api keys to run
- `pdf-muncher.py` (WIP): This will consume every PDF you put in the pdf-docs folder, and add it to the vectorized train.json

## Requirements

- boto3==1.34.119
- botocore==1.34.119
- bs4==0.0.2
- chardet==5.2.0
- httplib2==0.22.0
- jsonlines==4.0.0
- langchain==0.2.2
- langchain-aws==0.1.6
- langchain-community==0.2.2
- langchain-core==0.2.4
- langchain-pinecone==0.1.1
- langchain-text-splitters==0.2.1
- lxml==5.2.2
- pinecone==4.0.0
- pinecone-client==3.2.2
- python-dotenv==1.0.1
- requests==2.32.3
- tiktoken==0.7.0
- tqdm==4.66.4
- wget==3.2

## Usage

### Step 1 run /data_loader/run-locally.sh and follow prompts
Pre-requisites:
* URL=<the URL to rip>
* INDEX_NAME=<Pincone index name (must be existing)>
* PC_API_KEY=<Pinecone API Key (created when pinecone project is created)>
* CHUNK_SIZE=<data chunk size (choose 400 if uncertain)>
* CHUNK_OVERLAP=<chunk ovelap size (choose 40 if uncertain)>

This will run the python files in this order
get_website - Scrap website and extract only text
chunk_data - chunk data and prep for vector db
vectorize_upsert - Vectorize and loads vectors into pinecone vector db

### Step 2
Now we simply run rag_call.py and update line 13 with the question we want to pass the RAG call. 
* Pre-requisites = AWS Keys configured with Bedrock access