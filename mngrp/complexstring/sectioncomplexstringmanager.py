from FF8GameData.FF8HexReader.section import Section
from FF8GameData.gamedata import GameData, SectionType
from mngrp.complexstring.sectioncomplexstringentry import SectionComplexStringEntry
from mngrp.complexstring.sectionmapcomplexstring import SectionMapComplexString


class SectionComplexStringManager(Section):
    OFFSET_SIZE = 2
    HEADER_SIZE = 4

    def __init__(self, game_data: GameData, data_hex=bytearray(), id=0, own_offset=0, name=""):
        Section.__init__(self, game_data=game_data, data_hex=data_hex, id=id, own_offset=own_offset, name=name)

        self._nb_offset = 0
        self._map_section = None
        self._complex_string_entry_list = []
        self.type = SectionType.MNGRP_COMPLEX_STRING

    def add_map_section(self, map_section: SectionMapComplexString):
        self._map_section = map_section

    def add_string_entry(self, string_entry: SectionComplexStringEntry):
        print("Add entry")
        if not self._map_section:
            print("First add a map before adding string entry")
            return
        offset_list = self._map_section.get_offset_list_from_id(len(self._complex_string_entry_list))
        print(offset_list)
        string_entry.init_section(offset_list)
        #string_entry.init_text(offset_list)
        print(f"LEn: {len(self._complex_string_entry_list)}")
        print(string_entry)
        self._complex_string_entry_list.append(string_entry)

    def get_text_section_by_id(self, section_id):
        return self._complex_string_entry_list[section_id].get_text_section()
