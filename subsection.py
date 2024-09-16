from gamedata import GameData
from translation import Translation


class SubSection():
    def __init__(self, game_data: GameData, sub_section_id: int, sub_section_data: bytearray, sub_section_sub_offset: list):
        self.game_data = game_data
        self.sub_section_id = sub_section_id
        self.sub_section_data = sub_section_data
        self.sub_section_sub_offset = sub_section_sub_offset
        self.translation_list = []
        self.__analyze_data()

    def __analyze_data(self):
        for offset in self.sub_section_sub_offset:
            offset_value = int.from_bytes(self.sub_section_data[offset:offset + 2], byteorder="little")
            translation = Translation(game_data=self.game_data, offset_in_sub_section=offset, offset_value=offset_value)
            self.translation_list.append(translation)
