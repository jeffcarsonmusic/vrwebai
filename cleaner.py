import os
from bs4 import BeautifulSoup
import chardet
import shutil
import httplib2
import subprocess
from bs4 import BeautifulSoup, SoupStrainer

url = "https://dreamers.church"
# Set up the http object and make a request to the URL
http = httplib2.Http()
response, content = http.request(url)

# Parse the response and extract all first level linkss
links = []
for link in BeautifulSoup(content, parse_only=SoupStrainer('a'), features="html.parser"):
    if link.has_attr('href') and link['href'].startswith('/'):
        links.append(link['href'])

# Remove duplicates from list
unique_links = list(set(links))

for link in unique_links:
    print(link)
    
    # Concatenate the Church URL with the link from the list
    church_link = f'{url}{link}'
    
    # Check if wget is available
    wget_path = shutil.which("wget")
    if wget_path is None:
        print("wget is not installed or not in your PATH")
    else:
        # Define the wget command as a list of strings
        command = [
            wget_path,  # Use the full path to wget
            "-r",
            "-l", "2",
            "-nd",
            "-A", ".html,.txt,.tmp",
            "-P", "sitepages",
            church_link
        ]

        try:
            # Run the command
            result = subprocess.run(command, capture_output=True, text=True)
            # Check if the command was successful
            if result.returncode == 0:
                print("Command executed successfully")
                print(result.stdout)  # Output of the command
            else:
                print("Command failed with return code:", result.returncode)
                print(result.stderr)  # Error output of the command
        except FileNotFoundError as e:
            print(f"Command not found: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    print(f"Retrieving {church_link}")

# Function to get a unique filename if the file already exists
def get_unique_filename(file_path):
    base, ext = os.path.splitext(file_path)
    counter = 1
    while os.path.exists(file_path):
        file_path = f"{base}_{counter}{ext}"
        counter += 1
    return file_path

# Directory path to walk through
dir_path = 'sitepages'
output_dir = 'sitepages'  # Directory to save the parsed HTML files

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Loop through all subdirectories and files in the directory
for root, dirs, files in os.walk(dir_path, topdown=False):
    for filename in files:
        # Construct the full file path
        file_path = os.path.join(root, filename)

        # Check if the path is a file
        if os.path.isfile(file_path):
            try:
                # Detect the file's encoding using chardet
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    encoding = chardet.detect(raw_data)['encoding']

                # Read the file content with the detected encoding
                with open(file_path, 'r', encoding=encoding) as file:
                    file_content = file.read()


                # Create a BeautifulSoup object by opening the file directly
                with open(file_path, 'r', encoding=encoding) as file:
                    soup = BeautifulSoup(file, features="lxml")
                    doc_text = soup.get_text('\n')


                # Construct the output file path with .txt extension
                output_file_path = os.path.join(output_dir, os.path.basename(filename).split(".")[0] + ".txt")

                # Get a unique file name if the file already exists
                output_file_path = get_unique_filename(output_file_path)

                # Save the BeautifulSoup object to a file in UTF-8
                with open(output_file_path, 'w', encoding='utf-8') as file:
                    #remove empty lines
                    cleaned_lines = os.linesep.join([s for s in doc_text.splitlines() if s])
                    
                    file.write(str(cleaned_lines) + '\n')
                    

                # Delete the original file
                os.remove(file_path)

            except UnicodeDecodeError:
                print(f"Error decoding file: {file_path}")
            except Exception as e:
                print(f"An error occurred while processing file {file_path}: {e}")

    print("Processing completed.")

    # Delete the original directories
    for directory in dirs:
        shutil.rmtree(os.path.join(root, directory))