import dropbox
import requests

import os
from dotenv import load_dotenv
load_dotenv()

# Dropbox API access token
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
FOLDER_PATH = os.getenv('FOLDER_PATH')  # Specify the folder path you want to search
KEYWORDS = ['solar']
TAG = 'testing2'


# Initialize Dropbox client
dbx = dropbox.Dropbox(ACCESS_TOKEN)

def search_files_and_folders(keyword, path):
    """Search for files and folders containing a specific keyword in a specified folder."""
    try:
        results = dbx.files_search_v2(query=keyword, options=dropbox.files.SearchOptions(path=path))
        entries = results.matches
        return entries
    except dropbox.exceptions.ApiError as err:
        print(f"Failed to search files and folders with keyword '{keyword}' in folder '{path}': {err}")
        return []

def add_tag(path, tag_text):
    """Add a tag to a file or folder in Dropbox."""
    url = "https://api.dropboxapi.com/2/files/tags/add"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "path": path,
        "tag_text": tag_text
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Added tag '{tag_text}' to {path}")
    else:
        print(f"Failed to add tag '{tag_text}' to {path}: {response.json()}")

def main():
    for keyword in KEYWORDS:
        print(f"Searching for files and folders with keyword: {keyword} in folder: {FOLDER_PATH}")
        # Search for files and folders containing the keyword in the specified folder
        entries = search_files_and_folders(keyword, FOLDER_PATH)

        if not entries:
            print(f"No files or folders found with the keyword: {keyword} in folder: {FOLDER_PATH}")
            continue

        for entry in entries:
            metadata = entry.metadata.get_metadata()
            if isinstance(metadata, dropbox.files.FileMetadata) or isinstance(metadata, dropbox.files.FolderMetadata):
                path = metadata.path_lower
                print(f'Found entry: {metadata.name} (Path: {path})')
                add_tag(path, TAG)

if __name__ == '__main__':
    main()