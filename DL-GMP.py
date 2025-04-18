# Download all PDFs from URLs listed in dl-lists.txt and render base URL HTML as a PDF
import os
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
from weasyprint import HTML  # For rendering HTML as PDF

# Set environment variable for XDG_RUNTIME_DIR
os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-vscode"

# Base directory to save all files
base_dir = "Downloaded_Base_URLs"
os.makedirs(base_dir, exist_ok=True)

# Set the user agent to avoid being blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Counters for tracking progress
files_downloaded = 0
files_skipped = 0
files_failed = 0
urls_rendered = 0  # Counter for rendered URLs

# Function to download a file
def download_file(url, save_path):
    global files_downloaded, files_skipped, files_failed
    if os.path.exists(save_path):
        # Increment the skipped files counter without printing the message
        files_skipped += 1
        return
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        files_downloaded += 1
    else:
        print(f"Failed to download {url}")
        files_failed += 1

# Function to render and save the base URL HTML as a PDF
def render_html_as_pdf(base_url, output_dir, file_name="base_url_rendered.pdf"):
    global urls_rendered
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            html_save_path = os.path.join(output_dir, file_name)
            HTML(string=response.text).write_pdf(html_save_path)
            urls_rendered += 1  # Increment the rendered URLs counter
            print(f"HTML rendered and saved as PDF: {html_save_path}")
        else:
            print(f"Failed to fetch the URL for rendering: {base_url}")
    except Exception as e:
        print(f"Error rendering HTML as PDF: {e}")

# Function to process a single URL
def process_url(base_url):
    # Create a subdirectory for the base URL
    url_name = re.sub(r'[^\w\-]', '_', base_url)  # Replace invalid characters with '_'
    output_dir = os.path.join(base_dir, url_name)
    os.makedirs(output_dir, exist_ok=True)

    # Render the base URL HTML as a PDF
    render_html_as_pdf(base_url, output_dir)

    # Process and download all linked PDFs and pages within eur-lex.europa.eu/legal-content
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        # Find all links
        links = soup.find_all("a", href=True)
        for link in tqdm(links, desc=f"Processing links from {base_url}"):
            full_url = urljoin(base_url, link["href"])
            parsed_url = urlparse(link["href"])
            print(parsed_url)

            # If the link points to a PDF, download it
            if full_url.endswith(".pdf"):
                pdf_name = os.path.basename(full_url)
                save_path = os.path.join(output_dir, pdf_name)
                download_file(full_url, save_path)

            # If the link points to a page within eur-lex.europa.eu/legal-content, render it as a PDF
            elif "https://eur-lex.europa.eu/legal-content/EN/TXT/" in parsed_url:
                page_name = re.sub(r'[^\w\-]', '_', parsed_url.path) + ".pdf"
                render_html_as_pdf(full_url, output_dir, file_name=page_name)
    else:
        print(f"Failed to fetch the webpage: {base_url}")

# Read URLs from dl-list.txt and process each
with open("dl-list.txt", "r") as file:
    urls = file.readlines()

for url in urls:
    url = url.strip()  # Remove any leading/trailing whitespace
    if url:  # Skip empty lines
        process_url(url)

# Display counters
print("\nSummary:")
print(f"Files downloaded: {files_downloaded}")
print(f"Files skipped: {files_skipped}")
print(f"Files failed: {files_failed}")
print(f"URLs rendered: {urls_rendered}")