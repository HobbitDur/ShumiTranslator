from FF8GameData.FF8HexReader.section import Section
from FF8GameData.gamedata import GameData, SectionType
from FF8GameData.FF8HexReader.ff8text import FF8Text


class FF8SectionText(Section):
    def __init__(self, game_data: GameData, data_hex: bytearray, id: int, own_offset: int, name: str, section_data_linked=None, cursor_location_size=2):
        Section.__init__(self, game_data=game_data, data_hex=data_hex, id=id, own_offset=own_offset, name=name)
        self._text_list = []
        self.section_data_linked = section_data_linked
        self.type = SectionType.FF8_TEXT
        self.cursor_location_size = cursor_location_size

    def __str__(self):
        return "FF8SectionText : " + str(self._text_list)

    def __repr__(self):
        return self.__str__()

    def __bool__(self):
        return bool(self._text_list)

    def init_text(self, offset_list: list):
        if not offset_list:
            return
        for i, offset in enumerate(offset_list):
            if i == len(offset_list) - 1:  # Last one, compare with end of data
                next_offset = len(self._data_hex)
            else:
                next_offset = offset_list[i + 1]
                for j in range(i + 1, len(offset_list)):  # We are searching the next valid offset
                    if offset_list[j] != 0xFFFF:  # Unused data:
                        next_offset = offset_list[j]
                        break
            text_hex = self._data_hex[offset:next_offset]
            self.add_text(text_hex)

    def add_text(self, text_hex: bytearray):
        if self._text_list:
            offset = self._text_list[-1].own_offset + self._text_list[-1].get_size()
            id = self._text_list[-1].id + 1
        else:
            offset = 0
            id = 0
        self._text_list.append(FF8Text(game_data=self._game_data, data_hex=text_hex, own_offset=offset, id=id, cursor_location_size=self.cursor_location_size))

    def get_text_list(self):
        return self._text_list

    def get_text_from_id(self, id_text: int):
        return self._text_list[id_text].get_str()

    def update_data_hex(self):
        self._data_hex = bytearray()
        for data in self._text_list:
            self._data_hex.extend(data.get_data_hex())
        self._size = len(self._data_hex)
        return self._data_hex
