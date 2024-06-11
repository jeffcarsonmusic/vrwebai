#!/bin/sh
echo " "
echo "#######################################################"
echo "Welcome to the VR Suggested Response GenAI Quickstart!"
echo "#######################################################"
echo " "

# Get the website to scrape from the user
read -p "What website would you like to scrape?: " URL
while [ -z "$URL" ]; do
    echo "Website cannot be empty. Please provide a value."
    read -p "What website would you like to scrape?: " URL
done
echo " "

# Get the Pinecone index from the user
read -p "What Pinecone index to upsert the vectors to? " INDEX_NAME
while [ -z "$INDEX_NAME" ]; do
    echo "Pinecone index cannot be empty. Please provide a value."
    read -p "What Pinecone index to upsert the vectors to? " INDEX_NAME
done
echo " "

# Get the Pinecone API key from the user
read -p "What is the Pinecone API key? " PC_API_KEY
while [ -z "$PC_API_KEY" ]; do
    echo "Please enter your Pinecone API Key."
    read -p "What is the Pinecone API key? " PC_API_KEY
done
echo " "

# Get chunk size input from the user
read -p "What chunk size would you like to use? (enter 400 if uncertain) " CHUNK_SIZE
while [ -z "$CHUNK_SIZE" ]; do
    echo "Please enter a chunk size."
    read -p "What chunk size would you like to use? (enter 400 if uncertain) " CHUNK_SIZE
done
echo " "

# Get chunk overlap input from the user
read -p "What chunk overlap would you like to use? (enter 40 if uncertain) " CHUNK_OVERLAP
while [ -z "$CHUNK_OVERLAP" ]; do
    echo "Please enter a chunk overlap."
    read -p "What chunk overlap would you like to use? (enter 40 if uncertain) " CHUNK_OVERLAP
done
echo " "

# Create a .env file to store environment variables
touch .env
# Echo multiple environment variables to .env using a heredoc
cat << EOF >> .env
URL=$URL
INDEX_NAME=$INDEX_NAME
PC_API_KEY=$PC_API_KEY
CHUNK_SIZE=$CHUNK_SIZE
CHUNK_OVERLAP=$CHUNK_OVERLAP
EOF

# Load the environment variables
export $(cat .env | xargs)

# Check if the user has AWS access keys configured
read -p "Do you have AWS access keys configured? (y/n) " aws_keys
if [ "$aws_keys" = "n" ]; then
    echo "Please configure your AWS access keys locally before you continue."
    exit 1
else
    echo "Awesome! Let's continue."
    echo " "
    echo "Scraping website..."
    echo " "
fi

# Run the get website script to download the website and clean the text
python3 get_website.py
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "Script ran successfully."
else
    echo "Cleaner script encountered an error. Exit code: $exit_code"
    exit 1
fi

# Run the chunker script to chunk the website text into smaller pieces
python3 chunk_data.py
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo " "
    echo "Chunker script ran successfully. Let's vectorize the text chunks!"
    echo " "
else
    echo "Chunker script encountered an error. Exit code: $exit_code"
    exit 1
fi

# Run the vectorizer script to vectorize the text chunks and load into Pinecone
python3 vectorize_upsert.py 
exit_code=$?
if [ $exit_code -eq 0 ]; then    
    echo "Vectorizer script ran successfully. We're done!"
    exit 0
else
    echo "Vectorizer script encountered an error. Exit code: $exit_code"
    exit 1
fi

# Exit the script
exit 0