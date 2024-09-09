from gamedata import GameData
from kernel.kernelsection import KernelSection
from kernel.kerneltext import KernelText


class KernelSectionText(KernelSection):
    def __init__(self, game_data: GameData, data_hex: bytearray, id: int, own_offset: int, section_data_linked=None):
        KernelSection.__init__(self, game_data=game_data, data_hex=data_hex, id=id, own_offset=own_offset)
        self._text_list = []
        self.section_data_linked = section_data_linked
        self.type = "text"

    def init_text(self, offset_list: list):
        if not offset_list:
            print(f"No offset list to init for section id: {self.id}")
            return
        for i, offset in enumerate(offset_list):
            if i == len(offset_list):  # Last one, compare with end of data
                text_hex = self._data_hex[offset:len(self._data_hex)]
            else:
                text_hex = self._data_hex[offset:offset_list[i + 1]]
            self._text_list.append(self._game_data.translate_hex_to_str(text_hex))

    def add_text(self, text_hex: bytearray):
        if self._text_list:
            offset = self._text_list[-1].offset + self._text_list[-1].get_size()
        else:
            offset = 0
        self._text_list.append(KernelText(game_data=self._game_data, text_hex=text_hex, own_offset=offset))
