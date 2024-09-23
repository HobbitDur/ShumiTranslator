from sys import byteorder

from FF8GameData.gamedata import GameData, SectionType
from general.ff8data import FF8Data
from general.section import Section
from general.ff8sectiontext import FF8SectionText
from mngrp.complexstring.complexstringentry import ComplexStringEntry


class SectionComplexStringEntry(Section):

    def __init__(self, game_data: GameData, data_hex: bytearray, id: int, own_offset: int, name: str):
        Section.__init__(self, game_data=game_data, data_hex=data_hex, id=id, own_offset=own_offset, name=name)
        self.string_entry_list = []
        self.type = SectionType.MNGRP_COMPLEX_STRING

    def __str__(self):
        return f"SectionComplexStringEntry: {self.string_entry_list}"
    def __repr__(self):
        return self.__str__()

    def init_section(self, offset_map_list):
        print("init section")
        print(offset_map_list)
        for i, offset in enumerate(offset_map_list):
            if i == len(offset_map_list) - 1:
                next_offset = self._size
            else:
                next_offset = offset_map_list[i+1]
            new_entry = ComplexStringEntry(game_data= self._game_data, data_hex=self._data_hex[offset:next_offset], id=i, own_offset=offset, name="")
            self.string_entry_list.append(new_entry)
        print( self.string_entry_list)


    def get_text_list(self):
        entry_list = []
        for entry in self.string_entry_list:
            entry_list.append(entry.get_text_section().get_text_list()[0])
        print(f"Entry list: {entry_list}")
        return entry_list