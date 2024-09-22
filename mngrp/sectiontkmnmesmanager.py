import csv

from FF8GameData.gamedata import GameData
from general.ff8sectiontext import FF8SectionText
from general.section import Section, SectionType
from mngrp.sectiondata import SectionData


class SectionTkmnmesManager(Section):
    OFFSET_SIZE = 2
    HEADER_SIZE = 2

    def __init__(self, game_data: GameData, data_hex=bytearray(), id=0, own_offset=0, name=""):

        Section.__init__(self, game_data=game_data, data_hex=data_hex, id=id, own_offset=own_offset, name=name)

        self._nb_offset = 0
        self._offset_section = None
        self._text_section = None
        self.type = SectionType.MNGRP_STRING
        if data_hex:
            self.__analyse_data()

    def __str__(self):
        if not self._offset_section or not self._text_section:
            return "Empty section"
        return "StringManager offset: " + str(self._offset_section) + '\n' + "StringManager text: " + str(self._text_section)

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
        self._data_hex.extend(self._nb_offset.to_bytes(byteorder='little', length=2))
        self._data_hex.extend(self._offset_section.get_data_hex())
        self._text_section.update_text_data()
        self._data_hex.extend(self._text_section.get_data_hex())
        return self._data_hex

    def get_text_section(self):
        return self._text_section

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
        self._nb_offset = int.from_bytes(self._data_hex[0:self.HEADER_SIZE], byteorder='little')
        self._offset_section = SectionData(game_data=self._game_data,
                                           data_hex=self._data_hex[self.HEADER_SIZE:self._nb_offset * self.OFFSET_SIZE + self.HEADER_SIZE], id=0,
                                           own_offset=self.HEADER_SIZE, nb_offset=self._nb_offset, name="")

        first_offset = self._offset_section.get_all_offset()[0]
        text_data_start = first_offset
        text_data = self._data_hex[text_data_start:len(self._data_hex)]
        self._text_section = FF8SectionText(game_data=self._game_data, data_hex=text_data, id=self.id, own_offset=self.own_offset, name=self.name,
                                            section_data_linked=self._offset_section)
        self._text_section.section_data_linked.section_text_linked = self._text_section
        offset_list = self._offset_section.get_all_offset()
        for i in range(len(offset_list)):
            offset_list[i] -= self.HEADER_SIZE + self.OFFSET_SIZE * self._nb_offset
        self._text_section.init_text(offset_list)
        self.compute_data()  # To compute if there was offset removed (by removing offset with 0 value)

    def get_text_list(self):
        return self._text_section.get_text_list()

    def get_text_section(self):
        return self._text_section
