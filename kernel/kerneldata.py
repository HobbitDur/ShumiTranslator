from gamedata import GameData
from kernel.kernelsection import KernelSection


class KernelData(KernelSection):
    def __init__(self, game_data: GameData, own_offset: int, data_hex: bytearray, id: int, offset_type=False):
        KernelSection.__init__(self,  game_data=game_data, own_offset=own_offset, data_hex=data_hex, id=id)
        self._offset_type = offset_type

    def get_size(self):
        return self._size

    def get_offset_value(self):
        """We only analyze data that have an offset, the others are garbage data"""
        if self._offset_type:
            return int.from_bytes(self._data_hex, byteorder="little")
        else:
            return None
