import os
from langchain_community.document_loaders import ReadTheDocsLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm.auto import tqdm
import hashlib
import json
import tiktoken

# Variables
csize = os.getenv('CHUNK_SIZE', 400)
coverlap = os.getenv('CHUNK_OVERLAP', 20)

# The get_encoding function is called with the argument 'cl100k_base', 
# which is  the name of a specific encoding scheme. This function is 
# designed to return an Encoding object based on the provided encoding.
tokenizer = tiktoken.get_encoding('cl100k_base')

# 
def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)

def process_txt_files(folder_path):
    # Get all files in the folder
    all_files = os.listdir(folder_path)
    print("\n Found txt File: ", all_files)

    # Filter out txt files
    txt_files = [file for file in all_files if file.endswith('.txt')]

    # Initialize tokenizer and text_splitter
    tokenizer = tiktoken.get_encoding('cl100k_base')
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=csize,
        chunk_overlap=coverlap,
        length_function=tiktoken_len,
        separators=['\n\n', '\n', ' ', '']
    )

    documents = []

    # Process each txt file
    for txt_file in tqdm(txt_files):
        try:
            file_path = os.path.join(folder_path, txt_file)
            print("Chunking file: ", file_path)

            # Load the txt content
            with open(file_path, 'r') as f:
                content = f.read()

            # Generate a unique ID based on the file path
            m = hashlib.md5()
            m.update(file_path.encode('utf-8'))
            uid = m.hexdigest()[:12]

            # Split the content into chunks
            chunks = text_splitter.split_text(content)

            # Create document data
            for i, chunk in enumerate(chunks):
                documents.append({
                    'id': f'{uid}-{i}',
                    'text': chunk,
                    'source': file_path
                })

            # Delete the txt file after processing
            os.remove(file_path)

        except Exception as e:
            print(f"Error processing file {txt_file}: {e}")

    # Save the documents to a JSONL file
    with open('train.jsonl', 'a') as f:
        for doc in documents:
            f.write(json.dumps(doc) + '\n')

    return documents

# Call the function with the folder path "sitepages"
folder_path = "./sitepages"
documents = process_txt_files(folder_path)