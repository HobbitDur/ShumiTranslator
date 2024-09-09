from gamedata import GameData
from kernel.kerneldata import KernelData
from kernel.kernelsection import KernelSection


class KernelSectionHeader(KernelSection):
    OFFSET_SIZE = 4

    def __init__(self, game_data: GameData, data):
        KernelSection.__init__(self, game_data, data, 0, 0)
        self.__data_list = []
        self.analyze_data()

    def __add_data(self, data_hex):
        if self.__data_list:
            offset = self.__data_list[-1].offset + self.__data_list[-1].get_size()
        else:
            offset = 0
        self.__data_list.append(KernelData(game_data=self.__game_data, data_hex=data_hex, offset=offset))

    def analyze_data(self):
        for i in range(0, len(self.__data), self.OFFSET_SIZE):
            self.__add_data(self.__data[i:i + self.OFFSET_SIZE])
        if len(self.__data_list) != len(self.__game_data.kernel_data_json['sections']):
            print(
                f"Problem when analyzing data, the size is not what is expected: size_list: {len(self.__data_list)}, size expected: {len(self.__game_data.kernel_data_json['sections'])}")

    def get_section_offset_value_from_id(self, id):
        # This class as the ID 0, so thats why we do the ID -1
        if id < self.__data_list:
            return self.__data_list[id-1].get_int()
        else:
            print(f"Section ID unknown. Id: {}")
            return None