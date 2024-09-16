from gamedata import GameData


class KernelSection():
    def __init__(self, game_data: GameData, data_hex:bytearray, id:int, own_offset:int, name:str):
        self._data_hex = data_hex
        self._size = len(self._data_hex)
        self.id = id
        self._game_data = game_data
        self.own_offset = own_offset
        self.name = name
    def get_size(self):
        return self._size
    def __len__(self):
        return self._size
    def __str__(self):
        return f"KernelSection - OwnOffet: {self.own_offset} - data_hex: {self._data_hex.hex(sep=" ", bytes_per_sep=1)}"
