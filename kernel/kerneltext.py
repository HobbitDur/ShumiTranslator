from FF8GameData.gamedata import GameData
from kernel.kernelsection import KernelSection


class KernelText(KernelSection):
    def __init__(self, game_data: GameData, own_offset: int, text_hex: bytearray, id: int):
        KernelSection.__init__(self, game_data=game_data, own_offset=own_offset, data_hex=text_hex, id=id, name="")
        self._text_str = self._game_data.translate_hex_to_str(self._data_hex)

    def __str__(self):
        return f"KernelText: Text: {self._text_str} - bytes: {self._data_hex} - Hex: {self._data_hex.hex(sep=" ")}"

    def __repr__(self):
        return self.__str__()

    def get_str(self):
        return self._text_str

    def set_str(self, text: str):
        self._text_str = text
        self._data_hex = bytearray(self._game_data.translate_str_to_hex(self._text_str))
        if text != "":# If empty don't put \x00
            self._data_hex.extend([0x00])
        self._size = len(self._data_hex)
