# Description
This project involves controlling a network of bot computers using hidden messages transmitted through a shared Dropbox directory. Commands are sent to specific bots via a shared Dropbox account, ensuring the messages remain inconspicuous to the Dropbox owner. These commands are stealthily encoded using steganography techniques, such as embedding the messages in the pixels of images, or within video, mp3, or jar files.

# Instructions

1. Put the dropbox token into .env
2. Make sure you're in the root directory
3. Run the bots with `docker-compose up --build`
4. Run the controller via `python -m controller.controller ${DROPBOX_TOKEN}` or `python3 -m controller.controller ${DROPBOX_TOKEN}`
5. You should see the controller say `Conroller is aware of 3 bots`

# Sample run
1. `0: ls ./temp`
2. `0: copy controller/Controller.py` (now the file will be saved into the temp directory of the bot)
3. `0: ls ./temp` (now you should also see the `Controller.py` file there)
4. `1: id`
5. `1: w` (the docker doesn't have any users, so it probably returns an empty array)
6. `2: exec ./hello.sh` (you'll see the output in the bot console)

# Dependencies
In terms of dependencies for the controller.py, I think that this should be enough:

1. `pip install dropbox stegano psutil`
2. `apt-get update && apt-get install -y libgl1-mesa-glx`

# Supported commands: 
1. `[bot_num]: ls [path]?`
    - Returns the contents of [path] (or of `'.'` if [path] is not included).
    - C: Encodes the [path] into an image using stegano.
    - B: Decodes the [path] and sends back the result of `ls` using the same technique.
    - C: Decodes the result of `ls` and prints it.
2. `[bot_num]: w`
    - Returns the list of logged users.
    - C: Sends a random pdf to dropbox.
    - B: Notices that a pdf file has appeared and updates a `shopping_list.txt` with the encoded information.
    - B: Uploads a random video to indicate that the result is ready.
    - C: Extracts the users from the shopping list and prints it.
3. `[bot_num]: id`
    - Returns the uid if on linux, otherwise it returns 123.
    - C: Sends a random docx to dropbox.
    - B: Notices that a docx file has appeared and updates a `phone_numbers.txt` with the encoded information.
    - B: Sends a random jar file to indicate that the result is ready.
    - C: Extracts the uid from the list of phone numbers and prints it.
4. `[bot_num]: exec [path]`
    - Executes the file located at [path] in the bot directory.
    - C: Sends the [path] encoded in a large text file.
    - B: Decodes the [path] from the text file.
    - B: Executes the command and prints the result out.
5. `[bot_num]: copy [path]`
    - Copies the file from [path] into `./temp` in the bot directory.
    - C: Sends the entire file located at [path] encoded into an mp3 file using concatenation.
    - B: Extracts the file from the mp3 file and puts it in `./temp`
6. `exit`
    - Terminates the program

