from gamedata import GameData
from subsection import SubSection


class Section():
    def __init__(self, game_data: GameData, section_offset_value: int, section_offset_address: int, section_data: bytearray, nb_subsection: int,
                 subsection_size: int, section_name: str, sub_section_sub_offset: list):
        self.game_data = game_data
        self.section_offset_value = section_offset_value
        self.section_offset_address = section_offset_address
        self.section_data = section_data
        self.nb_subsection = nb_subsection
        self.subsection_size = subsection_size
        self.section_name = section_name
        self.sub_section_sub_offset = sub_section_sub_offset
        self.subsection_list = []
        self.__analyze_data()

    def __analyze_data(self):
        for sub_section_index in range(self.nb_subsection):
            start_index = sub_section_index * self.subsection_size
            sub_section = SubSection(game_data=self.game_data, sub_section_id=sub_section_index, sub_section_sub_offset=self.sub_section_sub_offset,
                                     sub_section_data=self.section_data[start_index: start_index + self.subsection_size])
            self.subsection_list.append(sub_section)
