from FF8GameData.gamedata import GameData
from general.ff8data import FF8Data
from general.section import Section
from general.ff8sectiontext import FF8SectionText


class SectionData(Section):
    OFFSET_SIZE = 2
    HEADER_SIZE = 2

    def __init__(self, game_data: GameData, data_hex: bytearray, id: int, own_offset: int, nb_offset: int, name: str,
                 section_text_linked: FF8SectionText = None):
        Section.__init__(self, game_data=game_data, data_hex=data_hex, id=id, own_offset=own_offset, name=name)
        self.section_text_linked = section_text_linked
        self._nb_offset = nb_offset
        self.type = "data"
        self._offset_list = []
        self.__analyse_data(nb_offset)

    def __str__(self):
        return "SectionData : " + str(self._offset_list)

    def __repr__(self):
        self.__str__()

    def __analyse_data(self, nb_offset):
        for i in range(nb_offset):
            data_offset = self._data_hex[i * self.OFFSET_SIZE:(i + 1) * self.OFFSET_SIZE]
            if data_offset != b'\x00\x00':  # offset at 0 are value to be ignored.
                new_data = FF8Data(game_data=self._game_data, own_offset=self.HEADER_SIZE + i * self.HEADER_SIZE,
                                   data_hex=data_offset, id=i,
                                   offset_type=True)
                self._offset_list.append(new_data)

    def get_all_offset(self):
        offset_list = []
        for ff8_data in self._offset_list:
            offset_list.append(ff8_data.get_offset_value())
        return offset_list

    def set_all_offset_value(self, text_list):
        if len(text_list) != self._nb_offset:
            print(
                f"The size of the offset list ({len(text_list)}) is different than the nb of offset data ({self._nb_offset})")

        current_offset = self._offset_list[0].get_offset_value()
        for i in range(len(text_list)):  # Assuming offset data is always at the beginning of the subsection
            text_size = len(text_list[i])
            self._offset_list[i].set_offset_value(current_offset)
            current_offset += text_size

        self._data_hex = bytearray()
        for ff8_data in self._offset_list:
            self._data_hex.extend(ff8_data.get_data_hex())
        self._size = len(self._data_hex)
