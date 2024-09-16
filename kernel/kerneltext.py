from gamedata import GameData
from kernel.kernelsection import KernelSection


class KernelText(KernelSection):
    def __init__(self, game_data: GameData, own_offset: int, text_hex: bytearray, id: int):
        KernelSection.__init__(self, game_data=game_data, own_offset=own_offset, data_hex=text_hex, id=id, name="")
        self._text_str = self._game_data.translate_hex_to_str(self._data_hex)

    def __str__(self):
        return f"KernelText : {self._text_str}"

    def __repr__(self):
        return self.__str__()

    def get_str(self):
        return self._text_str

    def set_str(self, text: str):
        print(f"Text str before: {self._data_hex}")
        self._text_str = text
        self._data_hex = bytearray(self._game_data.translate_str_to_hex(self._text_str))
        self._data_hex.extend([0x00])
        self._size = len(self._data_hex)
        print(f"Text str after: {self._data_hex}")
