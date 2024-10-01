import dropbox
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Load environment variables
ACCESS_TOKEN = os.getenv('TEAM_ACCESS_TOKEN')
FOLDER_PATH = os.getenv('TEAM_FOLDER_PATH')  # Specify the folder path you want to search
DROPBOX_ROOT_ID = os.getenv('DROPBOX_ROOT_ID')  # This can be found at the endpoint /users/get_current_account
TAG_TO_REMOVE = 'tenderresponse' # Specify the tag you want to remove

# Initialize Dropbox client
dbx = dropbox.Dropbox(ACCESS_TOKEN)

def list_folder_files(path, cursor=None):
    """List files in a folder, paginated using the list_folder API with or without a cursor."""
    url = "https://api.dropboxapi.com/2/files/list_folder/continue" if cursor else "https://api.dropboxapi.com/2/files/list_folder"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Dropbox-Api-Path-Root": f"{{\".tag\": \"root\", \"root\": \"{DROPBOX_ROOT_ID}\"}}"
    }
    data = {"cursor": cursor} if cursor else {"path": path, "recursive": True}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        results = response.json()
        return results
    except requests.exceptions.RequestException as err:
        print(f"Failed to list folder: {err}")
        return None

def get_tags(path):
    """Retrieve the tags for a given file or folder path."""
    url = "https://api.dropboxapi.com/2/files/tags/get"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Dropbox-Api-Path-Root": f"{{\".tag\": \"root\", \"root\": \"{DROPBOX_ROOT_ID}\"}}"
    }
    data = {
        "paths": [path],
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        results = response.json()

        paths_to_tags = results.get('paths_to_tags', [])
        if paths_to_tags:
            tags = paths_to_tags[0].get('tags', [])
            return [tag.get('tag_text').lower() for tag in tags if tag.get('.tag') == 'user_generated_tag']
        return []
    except requests.exceptions.RequestException as err:
        print(f"Failed to get tags for {path}: {err}")
        return []

def remove_tag(path, tag_text):
    """Remove a specific tag from a file or folder."""
    url = "https://api.dropboxapi.com/2/files/tags/remove"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Dropbox-Api-Path-Root": f"{{\".tag\": \"root\", \"root\": \"{DROPBOX_ROOT_ID}\"}}"
    }
    data = {
        "path": path,
        "tag_text": tag_text
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        if response.status_code == 200:
            print(f"Successfully removed tag '{tag_text}' from {path}")
    except requests.exceptions.RequestException as err:
        print(f"Failed to remove tag '{tag_text}' from {path}: {err}")

def process_files_in_folder(folder_path, tag_to_remove):
    """Search files, check for the tag, remove it if present, and continue searching."""
    result = list_folder_files(folder_path)
    if not result:
        print(f"Failed to retrieve files in folder: {folder_path}")
        return

    entries = result.get('entries', [])
    has_more = result.get('has_more', False)
    cursor = result.get('cursor', None)

    while True:
        for entry in entries:
            path = entry['path_display']
            name = entry['name']
            print(f'Processing file/folder: {name} (Path: {path})')

            # Get current tags for the file/folder
            existing_tags = get_tags(path)

            # Remove the specified tag if it exists
            if tag_to_remove in existing_tags:
                remove_tag(path, tag_to_remove)

        # Continue pagination if there are more files to process
        if has_more:
            result = list_folder_files(folder_path, cursor)
            if not result:
                break

            entries = result.get('entries', [])
            has_more = result.get('has_more', False)
            cursor = result.get('cursor', None)
        else:
            break

if __name__ == '__main__':
    process_files_in_folder(FOLDER_PATH, TAG_TO_REMOVE)
