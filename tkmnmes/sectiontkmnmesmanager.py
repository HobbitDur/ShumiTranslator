import csv

from FF8GameData.FF8HexReader.section import Section
from FF8GameData.gamedata import GameData, SectionType
from mngrp.sectiondata import SectionData
from mngrp.string.sectionstringmanager import SectionStringManager


class SectionTkmnmesManager(Section):
    OFFSET_SIZE = 2
    HEADER_SIZE = 2

    def __init__(self, game_data: GameData, data_hex=bytearray(), id=0, own_offset=0, name=""):

        Section.__init__(self, game_data=game_data, data_hex=data_hex, id=id, own_offset=own_offset, name=name)

        self._nb_padding = 0
        self._offset_section = None
        self._string_section_list = []
        self.type = SectionType.TKMNMES
        if data_hex:
            self.__analyse_data()

    def __str__(self):
        if not self._offset_section or not self._string_section_list:
            return "Empty section"
        return "SectionTkmnmesManager(offset_section: " + str(self._offset_section) + '\n' + "StringManager text: " + str(self._string_section_list) + ")"

    def load_file(self, file):
        current_file_data = bytearray()
        with open(file, "rb") as in_file:
            while el := in_file.read(1):
                current_file_data.extend(el)
        self._set_data_hex(current_file_data)
        self.__analyse_data()

    def save_file(self, file):
        self._offset_section.set_all_offset_value(self._text_section.get_text_list())

        self.compute_data()
        with open(file, "wb") as in_file:
            in_file.write(self._data_hex)

    def compute_data(self):
        self._data_hex = bytearray()
        self._data_hex.extend(self._nb_padding.to_bytes(byteorder='little', length=2))
        self._data_hex.extend(self._offset_section.get_data_hex())
        for section in self._string_section_list:
            section.compute_data()
            self._data_hex.extend(section.get_data_hex())
        return self._data_hex

    def save_csv(self, csv_path):
        if csv_path:
            with open(csv_path, 'w', newline='', encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

                csv_writer.writerow(
                    ['Text id', 'Text'])
                for ff8_text in self._text_section.get_text_list():
                    text_id = ff8_text.id
                    csv_writer.writerow([text_id, ff8_text.get_str()])

    def load_csv(self, csv_to_load, section_widget_list):
        if csv_to_load:
            with open(csv_to_load, newline='', encoding="utf-8") as csv_file:

                csv_data = csv.reader(csv_file, delimiter=';', quotechar='|')
                # ['Text id', 'Text']
                for row_index, row in enumerate(csv_data):
                    if row_index == 0:  # Ignoring title row
                        continue
                    text_id = int(row[0])
                    text_loaded = row[1]
                    # Managing this case as many people do the mistake.
                    text_loaded = text_loaded.replace('`', "'")
                    if text_loaded != "":  # If empty it will not be applied, so better be fast
                        for widget_index, widget in enumerate(section_widget_list):
                            section_widget_list[widget_index].set_text_from_id(text_id, text_loaded)

    def __analyse_data(self):
        self._nb_padding = int.from_bytes(self._data_hex[0:self.HEADER_SIZE], byteorder='little')
        end_offset_section = self._nb_padding * self.OFFSET_SIZE + self.HEADER_SIZE
        self._offset_section = SectionData(game_data=self._game_data,
                                           data_hex=self._data_hex[self.HEADER_SIZE:end_offset_section], id=0,
                                           own_offset=self.HEADER_SIZE, nb_offset=self._nb_padding, name="")
        offset_list = self._offset_section.get_all_offset()
        for i in range(len(offset_list)):
            if i == len(offset_list) - 1:
                next_string_section = len(self._data_hex)
            else:
                next_string_section = offset_list[i + 1]
            start_string_section = offset_list[i]
            self._string_section_list.append(
                SectionStringManager(game_data=self._game_data, data_hex=self._data_hex[start_string_section:next_string_section], id=self.id,
                                     own_offset=start_string_section, name=self.name + f" - subsection n°{i}"))
        self.compute_data()  # To compute if there was offset removed (by removing offset with 0 value)

    def get_nb_text_section(self):
        return len(self._string_section_list)

    def get_text_section_by_id(self, id):
        return self._string_section_list[id]

    def get_text_list(self):
        text_list = []
        for section_text in self._string_section_list:
            text_list.extend(section_text.get_text_list())
        return text_list
