from FF8GameData.gamedata import GameData
from general.ff8data import FF8Data
from general.ff8sectiontext import FF8SectionText
from general.ff8text import FF8Text
from general.section import Section


class SectionStringManager(Section):
    OFFSET_SIZE = 2
    HEADER_SIZE = 2

    def __init__(self, game_data: GameData):

        Section.__init__(self, game_data=game_data, data_hex=bytearray(), id=0, own_offset=0, name="")

        self._nb_offset = 0
        self._offset_list = []
        self._text_section = None
        self.__analyse_data()

    def load_file(self, file):
        current_file_data = bytearray()
        with open(file, "rb") as in_file:
            while el := in_file.read(1):
                current_file_data.extend(el)
        self._set_data_hex(current_file_data)
        self.__analyse_data()

    def __analyse_data(self):
        self._nb_offset = int.from_bytes(self._data_hex[0:self.HEADER_SIZE], byteorder='little')
        print(f"Nb offset: {self._nb_offset}")
        for i in range(self._nb_offset):
            data_offset = self._data_hex[i * self.OFFSET_SIZE:(i + 1) * self.OFFSET_SIZE]
            if data_offset != b'\x00\x00':  # offset at 0 are value to be ignored.
                new_data = FF8Data(game_data=self._game_data, own_offset=self.HEADER_SIZE + i * self.HEADER_SIZE,
                                   data_hex=data_offset, id=i,
                                   offset_type=True)
                self._offset_list.append(new_data)
        print(f"Offset list: { self._offset_list}")
        text_data_start = self._nb_offset * self.OFFSET_SIZE + 1
        text_data = self._data_hex[text_data_start:len(self._data_hex)]
        self._text_section = FF8SectionText(game_data=self._game_data, data_hex=text_data, id=0, own_offset=0, name="")
        curr_offset_list= []
        for ff8_data in self._offset_list:
            curr_offset_list.append(ff8_data.get_offset_value())
        self._text_section.init_text(curr_offset_list)
        print(self._text_section)
        self.compute_data()  # To compute if there was offset removed (by removing offset with 0 value)


    def compute_data(self):
        self._data_hex = bytearray()
        self._data_hex.extend(self._nb_offset.to_bytes(byteorder='little', length=2))
        for offset in self._offset_list:
            self._data_hex.extend(offset.get_data_hex())
        self._text_section.update_text_data()
        self._data_hex.extend(self._text_section.get_data_hex())
        print(self._data_hex)
        return self._data_hex

    def get_text_section(self):
        return self._text_section
