from gamedata import GameData
from kernel.kerneldata import KernelData
from kernel.kernelsection import KernelSection
from kernel.kerneltext import KernelText


class KernelSectionData(KernelSection):
    def __init__(self,game_data: GameData, data, id:int, offset:int, section_linked = None):
        KernelSection.__init__(self, game_data, data, id, offset)
        self.section_linked = section_linked
        self.__subsection_list = []

    def add_subsection(self, data_hex):
        if self.__subsection_list:
            offset = self.__subsection_list[-1].offset + self.__subsection_list[-1].get_size()
            id = self.__subsection_list[-1].id
        else:
            offset = 0
            id = 0
        self.__subsection_list.append(KernelData(game_data=self.__game_data, data_hex=data_hex, offset=offset, id=id))

