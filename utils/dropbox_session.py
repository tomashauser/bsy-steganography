import time

import dropbox
from dropbox.exceptions import ApiError


def get_nth_bot_dir(bot_number: int):
    return f'/Documents_{bot_number}'

# Used ChatGPT to help me with this
class DropboxSession:
    def __init__(self, access_token):
        self.dbx = dropbox.Dropbox(access_token)

    def upload_file(self, file_path, destination_path):
        with open(file_path, "rb") as file:
            try:
                self.dbx.files_upload(file.read(), destination_path, mode=dropbox.files.WriteMode.overwrite)
                print(f"File '{file_path}' uploaded successfully to '{destination_path}'", flush=True)
            except dropbox.exceptions.ApiError as error:
                print(f"An error occurred: {error}", flush=True)

    def get_files_list(self, folder_path=''):
        try:
            names = []
            entries = self.dbx.files_list_folder(folder_path).entries
            for entry in entries:
                names.append(entry.name)
            return names
        except dropbox.exceptions.ApiError as error:
            print(f"An error occurred: {error}", flush=True)
            return []

    def download_file(self, dropbox_path, local_path):
        print(f'Downloading a file from {dropbox_path} to {local_path}.', flush=True)
        try:
            self.dbx.files_download_to_file(local_path, dropbox_path)
            print(f"File '{dropbox_path}' downloaded successfully to '{local_path}'", flush=True)
        except dropbox.exceptions.ApiError as error:
            print(f"An error occurred: {error}", flush=True)

    def create_directory(self, folder_path):
        try:
            self.dbx.files_create_folder_v2(folder_path)
            print(f"Directory '{folder_path}' created successfully", flush=True)
        except dropbox.exceptions.ApiError as error:
            if isinstance(error.error,
                          dropbox.files.CreateFolderError) and error.error.is_path() and error.error.get_path().is_conflict():
                print(f"A directory at '{folder_path}' already exists.", flush=True)
            else:
                print(f"An error occurred: {error}", flush=True)

    def wait_for_new_file(self, folder_path, check_interval=1):
        print("Waiting for new file in:", folder_path, flush=True)

        previous_files = set(self.get_files_list(folder_path))
        while True:
            time.sleep(check_interval)  # Wait for specified interval

            current_files = set(self.get_files_list(folder_path))

            new_files = current_files - previous_files
            if new_files:
                print("New file(s) detected:", new_files, flush=True)
                return list(new_files)
            previous_files = current_files

    def delete_file(self, path):
        try:
            self.dbx.files_delete_v2(path)
            print("File or a folder at " + path + " has been deleted successfully")
        except dropbox.exceptions.ApiError as error:
            print("Couldn't delete a file or a folder: " + str(error), flush=True)

    def delete_everything_in_directory(self, dbx, directory):
        try:
            # List all items in the directory
            for entry in dbx.files_list_folder(directory).entries:
                try:
                    if isinstance(entry, dropbox.files.FileMetadata):
                        self.dbx.files_delete_v2(entry.path_lower)
                    elif isinstance(entry, dropbox.files.FolderMetadata):
                        self.dbx.files_delete_v2(entry.path_lower)
                except ApiError as e:
                    print(f"Error deleting {entry.path_lower}: {e}")
        except ApiError as e:
            print(f"Error accessing {directory}: {e}")

