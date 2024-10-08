import dropbox
import requests

import os
from dotenv import load_dotenv
load_dotenv()

# load environment variables
ACCESS_TOKEN = os.getenv('TEAM_ACCESS_TOKEN')
FOLDER_PATH = os.getenv('TEAM_FOLDER_PATH')  # Specify the folder path you want to search
DROPBOX_ROOT_ID = os.getenv('DROPBOX_ROOT_ID') # This can be found at the endpoint /users/get_current_account
KEYWORDS = ['methodology','method']
TAG = 'methodology'

# Initialize Dropbox client
dbx = dropbox.Dropbox(ACCESS_TOKEN)

def search_files_and_folders(keyword, path):
    """Search for files and folders containing a specific keyword in a specified folder."""
    url = "https://api.dropboxapi.com/2/files/search_v2"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Dropbox-Api-Path-Root": f"{{\".tag\": \"root\", \"root\": \"3211714451\"}}"
    }
    data = {
        "query": keyword,
        "options": {
            "path": path,
            "file_status": "active",
            "filename_only": True,
            "file_categories":[{".tag":"folder"},{".tag":"document"},{".tag":"pdf"},{".tag":"spreadsheet"},{".tag":"image"}]
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        results = response.json()
        return results.get('matches', [])
    except requests.exceptions.RequestException as err:
        print(f"Failed to search files and folders with keyword '{keyword}' in folder '{path}': {err}")
        print(err)
        return []

def get_tag(path):
    url = "https://api.dropboxapi.com/2/files/tags/get"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Dropbox-Api-Path-Root": f"{{\".tag\": \"root\", \"root\": \"{DROPBOX_ROOT_ID}\"}}"
    }
    data = {
        "paths": [path],
    }
    response = requests.post(url, headers=headers, json=data)
    results = response.json()

    tag_texts = []
    paths_to_tags = results.get('paths_to_tags', [])
    for path_data in paths_to_tags:
        tags = path_data.get('tags', [])
        for tag in tags:
            if tag.get('.tag') == 'user_generated_tag':
                tag_texts.append(tag.get('tag_text'))
    return tag_texts
    

def add_tag(path, tag_text):
    # Add a tag to a file or folder in Dropbox.
    url = "https://api.dropboxapi.com/2/files/tags/add"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Dropbox-Api-Path-Root": f"{{\".tag\": \"root\", \"root\": \"{DROPBOX_ROOT_ID}\"}}"
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
    count = 0
    for keyword in KEYWORDS:
        print(f"Searching for files and folders with keyword: {keyword} in folder: {FOLDER_PATH}")
        # Search for files and folders containing the keyword in the specified folder
        entries = search_files_and_folders(keyword, FOLDER_PATH)

        if not entries:
            print(f"No files or folders found with the keyword: {keyword} in folder: {FOLDER_PATH}")
            continue

        for entry in entries:
            metadata = entry['metadata']['metadata']
            path = metadata['path_display']
            name = metadata['name']
            print(f'Found entry: {name} (Path: {path})')

            # Check existing tags
            existing_tags = get_tag(path)
            if TAG in existing_tags:
                continue
                # print(f"Tag '{TAG}' already exists for {name} (Path: {path})")
            else:
                add_tag(path, TAG)
                count += 1
    print(f"Tagged {count} new files and folders.")

if __name__ == '__main__':
    main()