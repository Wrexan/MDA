import re

import bs4
import requests
from utility.utils import is_error_ignored


def is_update_available(ver_file_path: str, ver_url: str):
    """Version format is 0.0000"""
    try:
        update_page = requests.get(ver_url)
    except Exception as error:
        return False if is_error_ignored(error=error.__str__()) else error

    if update_page.status_code != 200:
        return update_page

    with open(ver_file_path, 'r', encoding='utf-8') as file:
        version_d = _version_str_to_number(file.readline())
    if version_d is None:
        return f"Can't load version file: {ver_file_path}"

    soup = bs4.BeautifulSoup(update_page.text, "html.parser")
    # MDA_0.7206.zip
    archive_name = soup.find(text=re.compile('MDA_')).text
    if archive_name:
        new_version_d = _version_str_to_number(archive_name[4:10])
        del soup
        return True if new_version_d > version_d else False
    else:
        return soup


def _version_str_to_number(version):
    version_sliced = version.split('.')
    if len(version_sliced) != 2 \
            or not version_sliced[0].isdigit() \
            or not version_sliced[1].isdigit():
        return
    return int(version_sliced[0]) * 10000 + int(version_sliced[1])
