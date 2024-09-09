from gamedata import GameData
from kernel.kerneldata import KernelData
from kernel.kernelsection import KernelSection
from kernel.kerneltext import *


class KernelSubSectionData(KernelSection):
    OFFSET_SIZE = 2

    def __init__(self, game_data: GameData, data_hex: bytearray, id: int, own_offset: int, nb_text_offset: int):
        KernelSection.__init__(self, game_data, data_hex, id, own_offset)
        self._nb_text_offset = nb_text_offset
        self._data_list = []
        self._analyze_data()

    def _analyze_data(self):
        """We consider the subsection to have N+1 data, with N data oof offset and 1 big data of whatever (the offset are always at the beggining)"""
        for i in range(self._nb_text_offset):
            self.add_data(self._data_list[i * self.OFFSET_SIZE: self.OFFSET_SIZE * (i + 1)], offset_type=True)
        self.add_data(self._data_list[(self._nb_text_offset + 1):], offset_type=False)

    def add_data(self, data_hex, offset_type=False):
        if self._data_list:
            offset = self._data_list[-1].own_offset + self._data_list[-1].get_size()
            id = self._data_list[-1].id + 1
        else:
            offset = 0
            id = 0
        self._data_list.append(KernelData(game_data=self._game_data, data_hex=data_hex, own_offset=offset, id=id, offset_type=offset_type))

    def get_all_offset(self):
        print("Get all offset subsection")
        offset_list = []
        print(f"self._data_list: {self._data_list}")
        for data in self._data_list:
            offset = data.get_offset_value()
            if offset:
                offset_list.append(offset)
        return offset_list
