from gamedata import GameData


class KernelSection():
    def __init__(self, game_data: GameData, data=bytearray(), id:int=0, offset:int=0):
        self.__data = data
        self.__size = len(self.__data)
        self.__id = id
        self.__game_data = game_data
        self.__offset = 0
