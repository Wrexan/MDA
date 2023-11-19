import os
import re
from copy import copy
from re import Match
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


def get_optimised_brands(main) -> tuple:
    # Getting all the brands other than current
    current_brand = main.curr_manufacturer.casefold()
    other_brands = copy(main.Price.BRANDS)
    other_brands.remove(current_brand)
    return current_brand, *other_brands


class DevicePart:
    part_name: str
    brand_name: str
    model_name: str
    note: str

    def __str__(self) -> str:
        return f'{self.part_name} {self.brand_name} {self.model_name} {self.note}'

    def parse_part_string(self, brands: tuple, compatibility_string: str) -> None:
        string = compatibility_string.casefold()
        # print(f'==={brands=}')
        # Splitting parts by 'или' will give the list of parts
        part_list = string.split('или')
        print(f'==={part_list=}')
        for part in part_list:
            part = part.strip()
            for brand in brands:
                brand_position = re.search(brand, part)
                if brand_position:
                    # If we found BRAND in part string
                    self.parse_part(part=part, brand=brand, brand_position=brand_position)
                else:
                    continue

    def parse_part(self, part: str, brand: str, brand_position: Match):
        brand_position_start = brand_position.start()
        brand_position_end = brand_position.end()
        model_note = part[brand_position_end:].strip()
        # print(f'==={model_note=}  {brand_position=}')
        # Will not make the part without a model
        if not model_note:
            return
        self.part_name = part[:brand_position_start].strip()
        self.brand_name = brand

        note_found = re.search(r'\(', model_note)
        if note_found:
            self.model_name = part[brand_position_end:brand_position_end + note_found.start()].strip()
            self.note = re.search(r'\((.*?)\)', part[note_found.end():]).group(1) or ''
        elif model_note:
            self.model_name = model_note
            self.note = ''

        print(f'------------------------------------------------------------------{self.__dict__=}')
