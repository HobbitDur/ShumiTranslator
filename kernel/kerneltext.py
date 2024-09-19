from lzma import compress

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
        converted_data_list = self._game_data.translate_str_to_hex(text)
        self._data_hex = bytearray(converted_data_list)
        self._text_str = text
        if text != "":  # If empty don't put \x00
            self._data_hex.extend([0x00])
        self._size = len(self._data_hex)

    def compress_str(self):
        compress_list = ["{in}", "{e }", "{ne}", "{to}", "{re}", "{HP}", "{l }", "{ll}", "{GF}", "{nt}", "{il}", "{o }",
                         "{ef}", "{on}", "{ w}", "{ r}", "{wi}", "{fi}", "{EC}", "{s }", "{ar}", "{FE}", "{ S}", "{ag}"]
        for compress_el in compress_list:
            if compress_el[1:-1] not in self._text_str:
                continue
            new_str_double_bracket = self._text_str.replace(compress_el[1:-1], compress_el)
            new_str_double_bracket = new_str_double_bracket.replace('{{', '{')
            new_str_double_bracket = new_str_double_bracket.replace('}}', '}')
            self.set_str(new_str_double_bracket)

    def uncompress_str(self):
        compress_list = ["{in}", "{e }", "{ne}", "{to}", "{re}", "{HP}", "{l }", "{ll}", "{GF}", "{nt}", "{il}", "{o }",
                         "{ef}", "{on}", "{ w}", "{ r}", "{wi}", "{fi}", "{EC}", "{s }", "{ar}", "{FE}", "{ S}", "{ag}"]
        for compress_el in compress_list:
            if compress_el not in self._text_str:
                continue
            self.set_str(self._text_str.replace(compress_el, compress_el[1:-1]))
