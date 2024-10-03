import csv

from FF8GameData.FF8HexReader.section import Section
from FF8GameData.gamedata import GameData, SectionType
from general.ff8sectiontext import FF8SectionText
from mngrp.sectiondata import SectionData


class SectionString(Section):
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
        else:
            self._offset_section = SectionData(game_data=game_data, data_hex=data_hex, id=0, own_offset=0, nb_offset=0,  name="")
            self._text_section = FF8SectionText(game_data=game_data, data_hex=data_hex, id=0, own_offset=0, name="")

    def __str__(self):
        if not self.__bool__():
            return "SectionStringManager(Empty)"
        return "SectionStringManager(offset_section: " + str(self._offset_section) + '\n' + "text_section: " + str(self._text_section) + ")"

    def __bool__(self):
        if not self._offset_section or not self._text_section:
            return False
        else:
            return True
    def __repr__(self):
        return self.__str__()

    def load_file(self, file):
        current_file_data = bytearray()
        with open(file, "rb") as in_file:
            while el := in_file.read(1):
                current_file_data.extend(el)
        self._set_data_hex(current_file_data)
        self.__analyse_data()

    def save_file(self, file):
        self._offset_section.set_all_offset_by_text_list(self._text_section.get_text_list())

        self.update_data_hex()
        with open(file, "wb") as in_file:
            in_file.write(self._data_hex)

    def update_data_hex(self):
        print(self._text_section.get_text_list())
        print(self._offset_section.get_all_offset())

        self._nb_offset= len(self._text_section.get_text_list()) # As some offset are ignored, changing the nb of offset
        self._nb_offset = 0x82
        self._text_section.update_data_hex()
        self._offset_section.set_all_offset_by_text_list(self._text_section.get_text_list(), shift = self.HEADER_SIZE +  self.OFFSET_SIZE * self._nb_offset)
        self._offset_section.update_data_hex()

        self._data_hex = bytearray()
        self._data_hex.extend(self._nb_offset.to_bytes(byteorder='little', length=2))
        self._data_hex.extend(self._offset_section.get_data_hex())
        for i in range(len(self._offset_section.get_all_offset()), self._nb_offset):
            self._data_hex.extend([0,0])
        self._data_hex.extend(self._text_section.get_data_hex())
        self._size = len(self._data_hex)
        return self._data_hex

    def get_text_section(self):
        return self._text_section

    def __analyse_data(self):
        print("Analysing data of sectionstringmanager")
        self._nb_offset = int.from_bytes(self._data_hex[0:self.HEADER_SIZE], byteorder='little')
        self._offset_section = SectionData(game_data=self._game_data,
                                           data_hex=self._data_hex[self.HEADER_SIZE:self._nb_offset * self.OFFSET_SIZE + self.HEADER_SIZE], id=0,
                                           own_offset=self.HEADER_SIZE, nb_offset=self._nb_offset, name="")
        if not self._offset_section:
            print(f"Empty offset")
        text_data_start = 0
        offset_list = self._offset_section.get_all_offset()
        #print(f"offset_list: {offset_list}")
        for offset in offset_list:
            if offset != 0:
                text_data_start = offset
                break
        text_data = self._data_hex[text_data_start:len(self._data_hex)]
        print(f"text_data_start: {text_data_start}")
        print(f"text_data_length: {len(text_data)}")
        #print(f"text_data: {text_data}")
        self._text_section = FF8SectionText(game_data=self._game_data, data_hex=text_data, id=self.id, own_offset=self.own_offset, name=self.name,
                                            section_data_linked=self._offset_section)
        self._text_section.section_data_linked.section_text_linked = self._text_section


        # The original offset start from the start of the section, so we need to shift them for the text offset.
        for i in range(len(offset_list)):
            offset_list[i] -= text_data_start
        self._text_section.init_text(offset_list)
        self._nb_offset = len(offset_list)
        if not self._text_section:
            print(f"Empty text")
        print(f"nb_offset: {self._nb_offset}")

    def get_text_list(self):
        return self._text_section.get_text_list()

