import requests
import os

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def download_database():
    db_file = 'all_data_scaled.db'
    if not os.path.exists(db_file):
        print("Database not found. Downloading...")
        file_id = import requests
import os

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)

def download_database():
    db_file = 'all_data_scaled.db'
    if not os.path.exists(db_file):
        print("Database not found. Downloading...")
        file_id = '1LuIkYQToXivEGHfn3v3dk8yq2qWD7gZm'  # Google Drive file ID
        destination = db_file
        download_file_from_google_drive(file_id, destination)
        print("Database downloaded successfully.")

if __name__ == "__main__":
    download_database()
'  # Google Drive file ID
        destination = db_file
        download_file_from_google_drive(file_id, destination)
        print("Database downloaded successfully.")

if __name__ == "__main__":
    download_database()
