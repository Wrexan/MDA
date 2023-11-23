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
    def __init__(self, part: str, brand: str, model: str, note: str):
        self.part: str = part
        self.brand: str = brand
        self.model: str = model
        self.note: str = note

    def __str__(self) -> str:
        return f'{self.part} {self.brand} {self.model}{f" ({self.note})" if self.note else ""}'

    def __repr__(self) -> str:
        return self.__str__()


def get_parts_by_parsing_string(brands: tuple, compatibility_string: str) -> [DevicePart] or None:
    string = compatibility_string.casefold()
    parsed_parts = []
    # Splitting parts by 'или' will give the list of parts
    stringed_parts = string.split('или')
    # print(f'==={stringed_parts=}')
    for part in stringed_parts:
        part = part.strip()
        for brand in brands:
            brand_position = re.search(brand, part)
            if brand_position:
                # If we found BRAND in part string
                parsed_part = parse_part(part=part, brand=brand, brand_position=brand_position)
                if not parsed_part:
                    continue
                for approved_part in parsed_parts:
                    if parsed_part.__dict__ == approved_part.__dict__:
                        break
                else:
                    parsed_parts.append(parsed_part)
            else:
                continue
    # print(f'==={parsed_parts=}')
    return parsed_parts if parsed_parts else None


def parse_part(part: str, brand: str, brand_position: Match):
    brand_position_start = brand_position.start()
    brand_position_end = brand_position.end()
    model_note = part[brand_position_end:].strip()
    # Will not make the part without a model
    if not model_note:
        return
    part_name = part[:brand_position_start].strip()

    note_found = re.search(r'\(', model_note)
    if note_found:
        model = part[brand_position_end:brand_position_end + note_found.start()].strip()
        note = ''  # re.search(r'\((.*?)\)', part[note_found.end():]).group(1) or ''
    else:
        model = model_note
        note = ''
    return DevicePart(part=part_name, brand=brand, model=model, note=note)

