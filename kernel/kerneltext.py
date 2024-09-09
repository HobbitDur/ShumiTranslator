from gamedata import GameData
from kernel.kernelsection import KernelSection


class KernelText(KernelSection):
    def __init__(self, game_data:GameData, own_offset:int, text_hex:bytearray, id:int):
        KernelSection.__init__(self,  game_data=game_data, own_offset=own_offset, data_hex=text_hex, id=id)
        self._text_str = self._game_data.translate_hex_to_str(self._data_hex)

