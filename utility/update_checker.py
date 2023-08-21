import re

import bs4
import requests


def is_update_available(ver_file_path: str, ver_url: str):
    """Version format is 0.0000"""
    update_page = requests.get(ver_url)
    if update_page.status_code != 200:
        return

    with open(ver_file_path, 'r', encoding='utf-8') as file:
        version_d = _version_str_to_number(file.readline())
    del file
    if version_d is None:
        return

    soup = bs4.BeautifulSoup(update_page.text, "html.parser")
    # MDA_0.7206.zip
    archive_name = soup.find(text=re.compile('MDA_')).text
    del soup
    new_version_d = _version_str_to_number(archive_name[4:10])
    if new_version_d > version_d:
        return True
    # return True  # ----------------------------------------


def _version_str_to_number(version):
    version_sliced = version.split('.')
    if len(version_sliced) != 2 \
            or not version_sliced[0].isdigit() \
            or not version_sliced[1].isdigit():
        return
    return int(version_sliced[0]) * 10000 + int(version_sliced[1])
