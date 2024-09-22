from FF8GameData.gamedata import GameData
from general.ff8data import FF8Data
from general.section import Section
from general.ff8sectiontext import FF8SectionText


class SeekLocationInfo():
    def __init__(self, seek_location: int, section_number: int):
        self.seek_location = seek_location
        self.section_number = section_number

    def __str__(self):
        return f"Seek_location: {str(self.seek_location)} - Section_number: {str(self.section_number)}"

    def __repr__(self):
        return self.__str__()


class SectionMapComplexString(Section):
    OFFSET_SIZE = 2
    HEADER_SIZE = 4
    SEEK_LOCATION_SIZE = 2
    SEEK_SECTION_NB_SIZE = 2

    def __init__(self, game_data: GameData, data_hex: bytearray, id: int, own_offset: int, name: str):
        Section.__init__(self, game_data=game_data, data_hex=data_hex, id=id, own_offset=own_offset, name=name)
        self._nb_seek_location = int.from_bytes(self._data_hex[0:self.HEADER_SIZE], byteorder="little")
        print(f"self._nb_seek_location: {self._nb_seek_location}")
        self._seek_location_info_list = []
        print("Analysing section map")
        for i in range(self._nb_seek_location):
            seek_location = int.from_bytes(self._data_hex[self.HEADER_SIZE + (self.SEEK_LOCATION_SIZE + self.SEEK_SECTION_NB_SIZE) * i:self.HEADER_SIZE + (
                    self.SEEK_LOCATION_SIZE + self.SEEK_SECTION_NB_SIZE) * i + self.SEEK_LOCATION_SIZE], byteorder="little")
            section_number = int.from_bytes(self._data_hex[self.HEADER_SIZE + (
                    self.SEEK_LOCATION_SIZE + self.SEEK_SECTION_NB_SIZE) * i + self.SEEK_LOCATION_SIZE:self.HEADER_SIZE + (
                    self.SEEK_LOCATION_SIZE + self.SEEK_SECTION_NB_SIZE) * i + self.SEEK_LOCATION_SIZE + self.SEEK_SECTION_NB_SIZE], byteorder="little")
            self._seek_location_info_list.append(SeekLocationInfo(seek_location, section_number))
        print("End Analysing section map")

    def __str__(self):
        return f"SectionMapComplexString: nb_seek:{self._nb_seek_location} - seek_info:{self._seek_location_info_list}"

    def __repr__(self):
        return self.__str__()

    def get_offset_list_from_id(self, section_id:int):
        offset_list= []
        for location_info in self._seek_location_info_list:
            if location_info.section_number ==section_id:
                offset_list.append(location_info.seek_location)

