from gamedata import GameData


class KernelData():
    def __init__(self, game_data:GameData, offset, data_hex:bytearray):
        self.__game_data = game_data
        self.offset = offset
        self.data_hex = data_hex
        self.__size = len(data_hex)
    def get_size(self):
        return self.__size
    def get_int(self):
        return int.from_bytes(self.data_hex, byteorder="little")
