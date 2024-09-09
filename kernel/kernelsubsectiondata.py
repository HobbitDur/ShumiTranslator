from gamedata import GameData
from kernel.kerneldata import KernelData
from kernel.kernelsection import KernelSection
from kernel.kerneltext import KernelText


class KernelSubSectionData(KernelSection):
    def __init__(self,game_data: GameData, data=bytearray(), id:int=0, offset:int=0):
        KernelSection.__init__(self, game_data, data, id, offset)
        self.data_list = []

    def add_data(self, data_hex):
        if self.data_list:
            offset = self.data_list[-1].offset + self.data_list[-1].get_size()
        else:
            offset = 0
        self.data_list.append(KernelData(game_data=self.__game_data, data_hex=data_hex, offset=offset))
