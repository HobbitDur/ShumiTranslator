from mngrp.complexstring.sectioncomplexstringentry import SectionComplexStringEntry
from mngrp.complexstring.sectioncomplexstringmanager import SectionComplexStringManager
from mngrp.complexstring.sectionmapcomplexstring import SectionMapComplexString
from mngrp.string.sectionstringmanager import SectionStringManager
import csv

from FF8GameData.gamedata import GameData, SectionType
from general.ff8sectiontext import FF8SectionText
from tkmnmes.sectiontkmnmesmanager import SectionTkmnmesManager


class MngrpManager():
    def __init__(self, game_data: GameData):
        self.game_data = game_data
        self.section_list = []
        self.section_complex_string = SectionComplexStringManager(game_data=self.game_data)

    def __str__(self):
        for section in self.section_list:
            print(section)

    def __repr__(self):
        return self.__str__()

    def save_file(self, file):
        current_offset = 0
        current_file_data = bytearray()

        # Then creating the file
        for index_section, section in enumerate(self.section_list):
            # First updating all offset on section data
            if section.type == "data" and section.section_text_linked:
                section_text_linked = section.section_text_linked
                section_text_list = section_text_linked.get_text_list()
                section.set_all_offset(section_text_list)
            # Then updating text
            if section.type == "text":
                section.update_text_data()
                self.section_list[0].set_section_offset_value_from_id(index_section, current_offset)
            current_offset += len(section)

        for section in self.section_list:
            current_file_data.extend(section.get_data_hex())
        with open(file, "wb") as in_file:
            in_file.write(current_file_data)

    def load_file(self, file):
        current_file_data = bytearray()
        with open(file, "rb") as in_file:
            while el := in_file.read(1):
                current_file_data.extend(el)
        # First we read all offset section
        self.section_list = []
        for index, section_info in enumerate(self.game_data.mngrp_data_json["sections"]):
            section_id = index
            section_offset_value = section_info["section_offset"]
            if index == len(self.game_data.mngrp_data_json["sections"]) - 1:
                next_section_offset_value = len(current_file_data)
            else:
                next_section_offset_value = self.game_data.mngrp_data_json["sections"][section_id + 1]['section_offset']
            own_offset = section_offset_value
            if section_info["data_type"] == SectionType.MNGRP_STRING:
                new_section = SectionStringManager(game_data=self.game_data, data_hex=current_file_data[own_offset:next_section_offset_value], id=section_id,
                                                   own_offset=own_offset, name=section_info['section_name'])
            elif section_info["data_type"] == SectionType.FF8_TEXT:
                new_section = FF8SectionText(game_data=self.game_data, id=section_id, own_offset=own_offset,
                                             data_hex=current_file_data[own_offset:next_section_offset_value],
                                             section_data_linked=None,
                                             name=section_info['section_name'])
            elif section_info["data_type"] == SectionType.TKMNMES:
                new_section = SectionTkmnmesManager(game_data=self.game_data, id=section_id, own_offset=own_offset,
                                                    data_hex=current_file_data[own_offset:next_section_offset_value],
                                                    name=section_info['section_name'])
            elif section_info["data_type"] == SectionType.MNGRP_MAP_COMPLEX_STRING:
                map_complex_string = SectionMapComplexString(game_data=self.game_data, id=section_id, own_offset=own_offset,
                                                             data_hex=current_file_data[own_offset:next_section_offset_value],
                                                             name=section_info['section_name'])
                self.section_complex_string.add_map_section(map_complex_string)
                new_section = None
            elif section_info["data_type"] == SectionType.MNGRP_COMPLEX_STRING:
                new_section = SectionComplexStringEntry(game_data=self.game_data, id=section_id, own_offset=own_offset,
                                                        data_hex=current_file_data[own_offset:next_section_offset_value],
                                                        name=section_info['section_name'])
                self.section_complex_string.add_string_entry(new_section)

            else:  # Just saving the data, but will not be modified
                new_section = Section(game_data=self.game_data, id=section_id, own_offset=own_offset,
                                      data_hex=current_file_data[own_offset:next_section_offset_value], name=section_info['section_name'])
                # new_section.init_subsection(nb_subsection=section_info['number_sub_section'], subsection_sized=section_info['sub_section_size'])
            if new_section:
                self.section_list.append(new_section)
        print(self.section_list)

    def save_csv(self, csv_path):
        if csv_path:
            with open(csv_path, 'w', newline='', encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

                csv_writer.writerow(
                    ['Section data name', 'Section data id', 'Sub section data id', 'Data id', 'Section text id',
                     'Text id', 'Text'])
                for index_section, section in enumerate(self.section_list):
                    if section.type == "data" and section.section_text_linked:
                        for sub_section in section.get_subsection_list():
                            for data in sub_section.get_data_list():
                                if data.get_offset_type():
                                    text_id = sub_section.id * \
                                              self.game_data.kernel_data_json["sections"][index_section - 1][
                                                  "sub_section_nb_text_offset"] + data.id
                                    csv_writer.writerow(
                                        [section.name, section.id, sub_section.id, data.id,
                                         section.section_text_linked.id, text_id,
                                         section.section_text_linked.get_text_from_id(text_id)])

    def load_csv(self, csv_to_load, section_widget_list):
        if csv_to_load:
            with open(csv_to_load, newline='', encoding="utf-8") as csv_file:

                csv_data = csv.reader(csv_file, delimiter=';', quotechar='|')
                # ['Section data name', 'Section data id', 'Sub section data id', 'Data id', 'Section text id', 'Text id', 'Text']
                for row_index, row in enumerate(csv_data):
                    if row_index == 0:  # Ignoring title row
                        continue

                    # section_data_id = int(row[1])
                    # sub_section_data_id = int(row[2])
                    # data_id = int(row[3])
                    section_text_id = int(row[4])
                    text_id = int(row[5])
                    text_loaded = row[6]
                    # Managing this case as many people do the mistake.
                    text_loaded = text_loaded.replace('`', "'")
                    if text_loaded != "":  # If empty it will not be applied, so better be fast
                        for widget_index, widget in enumerate(section_widget_list):
                            if widget.section.type == "text" and widget.section.id == section_text_id:
                                section_widget_list[widget_index].set_text_from_id(text_id, text_loaded)
