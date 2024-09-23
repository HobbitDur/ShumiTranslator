from sys import byteorder

from FF8GameData.gamedata import GameData, SectionType
from general.ff8data import FF8Data
from general.section import Section
from general.ff8sectiontext import FF8SectionText


class ComplexStringEntry(Section):
    UNK_SIZE = 6
    ENTRY_LENGTH = 2

    def __init__(self, game_data: GameData, data_hex: bytearray, id: int, own_offset: int, name: str):
        Section.__init__(self, game_data=game_data, data_hex=data_hex, id=id, own_offset=own_offset, name=name)
        self._unk = self._data_hex[0:self.UNK_SIZE]
        self._length = int.from_bytes(self._data_hex[self.UNK_SIZE:self.UNK_SIZE + self.ENTRY_LENGTH],
                                      byteorder='little')
        text_data_hex = self._data_hex[self.UNK_SIZE + self.ENTRY_LENGTH:]
        self._text_section = FF8SectionText(game_data=game_data, data_hex=text_data_hex, id=0, own_offset=0, name="")
        self._text_section.init_text([0])


    def __str__(self):
        return (
            f"SectionComplexStringEntry: unk:{self._unk.hex(sep=" ")} - length:{self._length} - text_section: {self._text_section}")

    def __repr__(self):
        return self.__str__()

    def init_text(self, offset_list):
        self._text_section.init_text(offset_list)

    def get_text_section(self):
        return self._text_section
