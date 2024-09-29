from FF8GameData.FF8HexReader.section import Section
from FF8GameData.gamedata import GameData, SectionType
from general.ff8sectiontext import FF8SectionText


class ComplexStringEntry(Section):
    TEXT_BOX_ID_SIZE = 2
    ENTRY_LENGTH = 2

    def __init__(self, game_data: GameData, data_hex: bytearray, id: int, own_offset: int, name: str):
        Section.__init__(self, game_data=game_data, data_hex=data_hex, id=id, own_offset=own_offset, name=name)
        self._text_box_origin_id = int.from_bytes(self._data_hex[0:self.TEXT_BOX_ID_SIZE], byteorder='little')
        self._text_box_left_id = int.from_bytes(self._data_hex[self.TEXT_BOX_ID_SIZE:self.TEXT_BOX_ID_SIZE * 2], byteorder='little')
        self._text_box_right_id = int.from_bytes(self._data_hex[self.TEXT_BOX_ID_SIZE * 2:self.TEXT_BOX_ID_SIZE * 3], byteorder='little')
        self._length = int.from_bytes(self._data_hex[self.TEXT_BOX_ID_SIZE * 3:self.TEXT_BOX_ID_SIZE * 3 + self.ENTRY_LENGTH],
                                      byteorder='little')
        text_data_hex = self._data_hex[self.TEXT_BOX_ID_SIZE * 3 + self.ENTRY_LENGTH:]
        print("text data hex !")
        print(text_data_hex)
        offset_end_title = text_data_hex.index(b'\x00')
        self._text_section = FF8SectionText(game_data=game_data, data_hex=text_data_hex, id=0, own_offset=0, name="", cursor_location_size=3)
        self._text_section.init_text([0, offset_end_title])
        print(f"self._text_section: {self._text_section}")

    def __str__(self):
        return (
            f"SectionComplexStringEntry: Ori:{self._text_box_origin_id} - left:{self._text_box_left_id} -right:{self._text_box_right_id} - length:{self._length} - text_section: {self._text_section}")

    def __repr__(self):
        return self.__str__()

    def get_text_section(self):
        return self._text_section

    def update_data_hex(self):
        self._data_hex = bytearray()
        self._data_hex.extend(self._text_box_origin_id.to_bytes(length=self.TEXT_BOX_ID_SIZE, byteorder='little'))
        self._data_hex.extend(self._text_box_left_id.to_bytes(length=self.TEXT_BOX_ID_SIZE, byteorder='little'))
        self._data_hex.extend(self._text_box_right_id.to_bytes(length=self.TEXT_BOX_ID_SIZE, byteorder='little'))
        self._data_hex.extend(self._length.to_bytes(length=self.ENTRY_LENGTH, byteorder='little'))
        self._text_section.update_data_hex()
        self._data_hex.extend(self._text_section.get_data_hex())
        self._size = len(self._data_hex)

