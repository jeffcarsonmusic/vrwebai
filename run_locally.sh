#!/bin/sh
echo " "
echo "#######################################################"
echo "Welcome to the VR Suggested Response GenAI Quickstart!"
echo "#######################################################"
echo " "

# Get the website to scrape from the user
read -p "What website would you like to scrape?: " url
while [ -z "$url" ]; do
    echo "Website cannot be empty. Please provide a value."
    read -p "What website would you like to scrape?: " url
done
echo " "

# Get the Pinecone index from the user
read -p "What Pinecone index to upsert the vectors to? " pc_index
while [ -z "$pc_index" ]; do
    echo "Pinecone index cannot be empty. Please provide a value."
    read -p "What Pinecone index to upsert the vectors to? " pc_index
done
touch .env
# Save the Pinecone index to the .env file
echo INDEX_NAME=$pc_index >> .env
echo " "

# Get the Pinecone API key from the user
read -p "What is the Pinecone API key? " pc_api_key
while [ -z "$pc_api_key" ]; do
    echo "Please enter your Pinecone API Key."
    read -p "What is the Pinecone API key? " pc_api_key
done

# Save the Pinecone API key to the .env file
echo PINECONE_API_KEY=$pc_api_key >> .env
echo " "

# Get chunk size input from the user
read -p "What chunk size would you like to use? (enter 1000 if uncertain) " chunk_size
while [ -z "$chunk_size" ]; do
    echo "Please enter a chunk size."
    read -p "What chunk size would you like to use? (enter 1000 if uncertain) " chunk_size
done
echo " "

# Get chunk overlap input from the user
read -p "What chunk overlap would you like to use? (enter 100 if uncertain) " chunk_overlap
while [ -z "$chunk_overlap" ]; do
    echo "Please enter a chunk overlap."
    read -p "What chunk overlap would you like to use? (enter 100 if uncertain) " chunk_overlap
done
echo " "

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

# Run the cleaner script to download the website and clean the text
python3 cleaner.py "$url"
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "Script ran successfully."
else
    echo "Cleaner script encountered an error. Exit code: $exit_code"
    exit 1
fi

# Run the chunker script to chunk the website text into smaller pieces
python3 chunker.py "$chunk_size" "$chunk_overlap" "$url"
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
python3 vectorizer.py "$chunk_size" "$chunk_overlap" "$url"
exit_code=$?
if [ $exit_code -eq 0 ]; then
    # Clean up local directory structure
    rm -rf .env train.jsonl sitepages
    echo "Vectorizer script ran successfully. We're done!"
    exit 0
else
    echo "Vectorizer script encountered an error. Exit code: $exit_code"
    exit 1
fi

# Exit the script
exit 0