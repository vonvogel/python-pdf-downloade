import requests

# Save the URL to a variable
url = "https://www.uu.se"

# Define the endpoint
endpoint = "http://weasyprint:5001/pdf"

# Fetch the body of the URL
response_get = requests.get(url)
if response_get.status_code == 200:
    body = response_get.text  # Get the HTML content of the page
else:
    print(f"Failed to fetch the URL. Status code: {response_get.status_code}, Response: {response_get.text}")
    exit()

# Send the body as a POST request
response_post = requests.post(endpoint, body)

# Check if the response is successful
if response_post.status_code == 200:
    # Save the received PDF to a file
    with open("output.pdf", "wb") as pdf_file:
        pdf_file.write(response_post.content)
    print("PDF received and saved as 'output.pdf'")
else:
    print(f"Failed to receive PDF. Status code: {response_post.status_code}, Response: {response_post.text}")