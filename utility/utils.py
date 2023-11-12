import os
from datetime import datetime
from utility.config import ERROR_FOLDER_PATH, ERRORS_TO_IGNORE


def check_and_create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def save_error_file(data: str):
    check_and_create_folder(ERROR_FOLDER_PATH)
    file_name = f'Error [{datetime.now().strftime("%Y%m%d-%H_%M_%S")}]'
    print(f'saving error file: {file_name}')
    with open(os.path.join(ERROR_FOLDER_PATH, file_name), 'w') as file:
        file.write(data)


def is_error_ignored(error: str):
    for err_type in ERRORS_TO_IGNORE:
        if err_type in error.__str__():
            return True
