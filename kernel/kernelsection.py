from gamedata import GameData


class KernelSection():
    def __init__(self, game_data: GameData, data_hex:bytearray, id:int, own_offset:int):
        self._data_hex = data_hex
        self._size = len(self._data_hex)
        self.id = id
        self._game_data = game_data
        self.own_offset = own_offset
    def get_size(self):
        return self._size
