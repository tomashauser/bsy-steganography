import shutil
import subprocess
import psutil
import os

import requests


def get_files(path: str) -> [str]:
    return os.listdir(path)


def get_logged_users() -> [str]:
    users = psutil.users()
    usernames = []
    for user in users:
        usernames.append(user.name)
    return usernames


def write_file(path: str, data):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(data)


def get_user_id() -> int:
    try:
        return os.getuid()
    except AttributeError as e:
        print("Windows has no uid, returning some random value")
        return 123



def count_files_in_directory(directory):
    # Count the number of files in the specified directory
    try:
        return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])
    except FileNotFoundError:
        print(f"Directory not found: {directory}")
        return 0


def delete_contents_of_folder(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a directory or does not exist.")
        return

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # remove file or link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # remove directory
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


def get_nth_file(directory, n):
    try:
        # List all files and directories in the given directory
        files_and_directories = os.listdir(directory)

        # Filter out directories, keep only files
        files = [f for f in files_and_directories if os.path.isfile(os.path.join(directory, f))]

        # Return the nth file
        return files[n]
    except FileNotFoundError:
        print(f"Directory not found: {directory}")
        return None
    except IndexError:
        print(f"There is no file at position {n}.")
        return None


def download_image(url, filename):
    response = requests.get(url)

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Image successfully downloaded: {filename}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")


def read_file_contents(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None


def run_binary(path_to_file):
    try:
        # Run the command and capture output and error
        result = subprocess.run([path_to_file], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Print the output and error
        print("Output:", result.stdout)
        print("Error:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("An error occurred:", e)
