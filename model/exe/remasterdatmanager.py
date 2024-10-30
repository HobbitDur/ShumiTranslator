import os
import pathlib

from FF8GameData.ExeSection.exefile import SectionExeFile
import csv

from FF8GameData.GenericSection.offsetandtext import SectionOffsetAndText
from FF8GameData.GenericSection.sizeandoffsetandtext import SectionSizeAndOffsetAndText
from FF8GameData.gamedata import GameData, LangType, RemasterCardType



class RemasterDatManager:
    def __init__(self, game_data: GameData):
        self.game_data = game_data

        self._section = None
        self._lang = LangType.ENGLISH

    def __str__(self):
        return str(self._section)

    def __repr__(self):
        return self.__str__()

    def get_section(self) -> SectionSizeAndOffsetAndText:
        return self._section

    def save_file(self, file_dat):
        self._section.update_data_hex()
        with open(file_dat, "wb") as f:
            f.write(self._section.get_data_hex())

    def load_file(self, file_to_load, remaster_type: RemasterCardType):
        file_name = pathlib.Path(file_to_load).name
        file_data = bytearray()
        with open(file_to_load, "rb") as file:
            file_data.extend(file.read())
        if remaster_type == RemasterCardType.CARD_NAME:
            self._section = SectionSizeAndOffsetAndText(self.game_data, file_data, id=0, own_offset=0, name=file_name, ignore_empty_offset=False)
        elif remaster_type == RemasterCardType.CARD_NAME2:
            self._section = SectionOffsetAndText(self.game_data, file_data, id=0, own_offset=0, name=file_name, ignore_empty_offset=False)

        if "en" in file_name:
            self._lang = LangType.ENGLISH
        elif "it" in file_name:
            self._lang = LangType.ITALIAN
        elif "es" in file_name:
            self._lang = LangType.SPANISH
        elif "fr" in file_name:
            self._lang = LangType.FRENCH
        elif "de" in file_name:
            self._lang = LangType.GERMAN

    def save_csv(self, csv_path):
        if csv_path:
            with open(csv_path, 'w', newline='', encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=GameData.find_delimiter_from_csv_file(csv_path), quotechar='|', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(
                    ['Section data name', 'Section id', 'Text Sub id', 'Text'])
                card_name_section = self._section
                for card_index, card_ff8_text in enumerate(card_name_section.get_text_section().get_text_list()):
                    csv_writer.writerow([card_name_section.name, card_name_section.id, card_index, card_ff8_text.get_str()])

    def load_csv(self, csv_to_load, section_widget_list):
        if csv_to_load:
            with open(csv_to_load, newline='', encoding="utf-8") as csv_file:
                csv_data = csv.reader(csv_file, delimiter=GameData.find_delimiter_from_csv_file(csv_to_load), quotechar='|')
                #  ['Section data name', 'Section id', 'Text Sub id', 'Text']
                for row_index, row in enumerate(csv_data):
                    if row_index == 0:  # Ignoring title row
                        continue
                    # section_data_name = row[0]
                    section_id = int(row[1])
                    text_sub_id = int(row[2])
                    text_loaded = row[3]

                    if text_loaded == "":
                        continue
                    # Managing this case as many people do the mistake.
                    text_loaded = text_loaded.replace('`', "'")
                    for widget_index, widget in enumerate(section_widget_list):
                        if widget.section.id == section_id:
                            section_widget_list[widget_index].set_text_from_id(text_sub_id, text_loaded)
                            break
