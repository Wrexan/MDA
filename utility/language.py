import json
from dataclasses import dataclass


@dataclass
class Language:
    def __init__(self, config):
        self.C = config
        self.load_language()

    def load_language(self):
        with open(f'{self.C.LANG_PATH}\\{self.C.CURRENT_LANG}', 'r', encoding='utf-8') as f:
            lang_data = json.load(f)
        for text_elem in lang_data.items():
            self.__setattr__(*text_elem)
