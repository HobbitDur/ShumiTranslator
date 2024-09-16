from gamedata import GameData
from kernel.kerneldata import KernelData
from kernel.kernelsection import KernelSection
from kernel.kernelsectiontext import KernelSectionText
from kernel.kernelsubsectiondata import KernelSubSectionData
from kernel.kerneltext import KernelText


class KernelSectionData(KernelSection):
    def __init__(self, game_data: GameData, data_hex: bytearray, id: int, own_offset: int, subsection_nb_text_offset: int, name:str,
                 section_text_linked: KernelSectionText = None):
        KernelSection.__init__(self, game_data=game_data, data_hex=data_hex, id=id, own_offset=own_offset, name=name)
        self._subsection_nb_text_offset = subsection_nb_text_offset
        self.section_text_linked = section_text_linked
        self._subsection_list = []
        self.type = "data"

    def init_subsection(self, subsection_sized: int, nb_subsection: int):
        for i in range(nb_subsection):
            self.add_subsection(self._data_hex[i * subsection_sized: (i+1) * subsection_sized])

    def add_subsection(self, data_hex: bytearray):
        if self._subsection_list:
            offset = self._subsection_list[-1].own_offset + self._subsection_list[-1].get_size()
            id = self._subsection_list[-1].id
        else:
            offset = 0
            id = 0
        self._subsection_list.append(
            KernelSubSectionData(game_data=self._game_data, data_hex=data_hex, own_offset=offset, id=id, nb_text_offset=self._subsection_nb_text_offset))

    def get_all_offset(self):
        offset_list = []
        for subsection in self._subsection_list:
            offset_list.extend(subsection.get_all_offset())
        return offset_list