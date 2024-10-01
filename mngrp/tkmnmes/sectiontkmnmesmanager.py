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
        return f"SectionTkmnmesManager(nb_padding: {self._nb_padding}, \n offset_section: {str(self._offset_section)} \n StringManager text section list: {str(self._string_section_list)}"

    def __repr__(self):
        return self.__str__()

    def load_file(self, file_to_load):
        self._data_hex = bytearray()
        with open(file_to_load, "rb") as file:
            self._data_hex.extend(file.read())
        self.__analyse_data()

    def __analyse_data(self):
        self._nb_padding = int.from_bytes(self._data_hex[0:self.HEADER_SIZE], byteorder='little') +1
        print(f"nb_padding: {self._nb_padding}")
        end_offset_section = self._nb_padding * self.OFFSET_SIZE + self.HEADER_SIZE
        print(f"end_offset_section: {end_offset_section}")
        self._offset_section = SectionData(game_data=self._game_data,
                                           data_hex=self._data_hex[self.HEADER_SIZE:end_offset_section], id=0,
                                           own_offset=self.HEADER_SIZE, nb_offset=self._nb_padding, name="")
        print(f"self._offset_section: {self._offset_section}")

        offset_list = self._offset_section.get_all_offset()
        print(f"Toto offset list: {offset_list}")
        for i in range(len(offset_list)):
            print(f"Yes i : {i}")
            if i == len(offset_list) - 1:
                next_string_section = len(self._data_hex)
            else:
                next_string_section = 0
                for j in range(i+1, len(offset_list)):
                    if offset_list[j] != 0:
                        next_string_section = offset_list[j]
                        break
                if next_string_section == 0:
                    next_string_section = len(self._data_hex)

            start_string_section = offset_list[i]
            print(f"start_string_section: {start_string_section}")
            print(f"next_string_section: {next_string_section}")
            if next_string_section == 0:
                print("Unexpected empty next offset in tkmnmes manager")
                continue
            else:
                print("Building string")

                string_data_hex = self._data_hex[start_string_section:next_string_section]
                new_section = SectionStringManager(game_data=self._game_data, data_hex=string_data_hex, id=i,
                                         own_offset=start_string_section, name=self.name + f" - subsection n°{i}")
                self._string_section_list.append(new_section)
                print(f"new section: {new_section}")

    def update_data_hex(self):
        new_padding_list = []
        # First we update all string section, so we can compute the padding
        shift_padding = self.HEADER_SIZE + self.OFFSET_SIZE* self._nb_padding
        for i in range(len(self._string_section_list)):
            print(f"len(self._string_section_list[i]): {len(self._string_section_list[i])}")
            self._string_section_list[i].update_data_hex()
            print(f"len(self._string_section_list[i]): {len(self._string_section_list[i])}")
            new_padding_list.append(shift_padding)
            shift_padding+=len(self._string_section_list[i])
        self._offset_section.set_all_offset_by_value_list(new_padding_list)

        self._data_hex = bytearray()
        self._data_hex.extend((self._nb_padding-1).to_bytes(byteorder='little', length=2))
        self._data_hex.extend(self._offset_section.get_data_hex())
        for i in range(len(self._string_section_list)):
            self._data_hex.extend( self._string_section_list[i].get_data_hex())
        self._size = len(self._data_hex)
        return self._data_hex

    def get_nb_text_section(self):
        return len(self._string_section_list)

    def get_text_section_by_id(self, id):
        return self._string_section_list[id]

    def get_text_list(self):
        text_list = []
        for section_text in self._string_section_list:
            text_list.extend(section_text.get_text_list())
        return text_list
