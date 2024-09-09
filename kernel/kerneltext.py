from gamedata import GameData


class KernelText():
    def __init__(self, game_data:GameData, offset =0, text_hex=bytearray()):
        self.__game_data = game_data
        self.offset = offset
        self.__text_hex = text_hex
        self.__text_str = self.__game_data.translate_hex_to_str(self.__text_hex)
        self.__size = len(text_hex)
    def get_size(self):
        return self.__size
