from FF8GameData.FF8HexReader.mngrp import Mngrp
from FF8GameData.FF8HexReader.mngrphd import Mngrphd
from mngrp.complexstring.sectioncomplexstringentry import SectionComplexStringEntry
from mngrp.complexstring.sectioncomplexstringmanager import SectionComplexStringManager
from mngrp.complexstring.sectionmapcomplexstring import SectionMapComplexString
from mngrp.m00x.sectionm00bin import Sectionm00Bin
from mngrp.string.sectionstringmanager import SectionStringManager
import csv

from FF8GameData.gamedata import GameData, SectionType
from general.ff8sectiontext import FF8SectionText
from mngrp.tkmnmes.sectiontkmnmesmanager import SectionTkmnmesManager


class MngrpManager:
    def __init__(self, game_data: GameData):

        self.mngrphd = None
        self.mngrp = None
        self.game_data = game_data
        self.section_complex_string = SectionComplexStringManager(game_data=self.game_data)

    def __str__(self):
        return str(self.mngrp)

    def __repr__(self):
        return self.__str__()

    def save_file(self, file_mngrp, file_mngrphd):
        current_offset = 0
        current_file_data = bytearray()

        # Then creating the file
        #for index_section, section in enumerate(self.mngrp.get_section_list()):
        #    if section.type == SectionType.TKMNMES:
        #        section.update_data_hex()
        self.mngrp.update_data_hex()
        #for index_section, section in enumerate(self.mngrp.get_section_list()):
        #    # First updating all offset on section data
        #    if section.type == SectionType.DATA and section.section_text_linked:
        #        section_text_linked = section.section_text_linked
        #        section_text_list = section_text_linked.get_text_list()
        #        section.set_all_offset(section_text_list)
        #    # Then updating text
        #    if section.type == SectionType.FF8_TEXT:
        #        section.update_text_data()
        #    current_offset += len(section)

        with open(file_mngrp, "wb") as in_file:
            in_file.write(self.mngrp.get_data_hex())
        with open(file_mngrphd, "wb") as in_file:
            in_file.write(self.mngrphd.get_data_hex())

    def load_file(self, file_mngrphd, file_mngrp):
        mngrphd_data_hex = bytearray()
        mngrp_data_hex = bytearray()
        with open(file_mngrphd, "rb") as file:
            mngrphd_data_hex.extend(file.read())
        with open(file_mngrp, "rb") as file:
            mngrp_data_hex.extend(file.read())

        self.mngrphd = Mngrphd(self.game_data, mngrphd_data_hex)
        self.mngrp = Mngrp(self.game_data, mngrp_data_hex, self.mngrphd.get_entry_list())

        # First we read all offset section
        m00bin_counter = 0
        m00msg_counter = 0
        for index, section_mngrp in enumerate(self.mngrp.get_section_list()):
            if self.mngrphd.get_entry_list()[index].invalid_value: # If it's a non-existent section, ignore it
                continue
            section_id = section_mngrp.id
            section_data_type = self.game_data.mngrp_data_json["sections"][section_id]["data_type"]
            section_name = self.game_data.mngrp_data_json["sections"][section_id]["section_name"]
            section_offset_value = section_mngrp.own_offset
            section_data_hex = section_mngrp.get_data_hex()
            if section_data_type == SectionType.MNGRP_STRING:
                new_section = SectionStringManager(game_data=self.game_data, data_hex=section_data_hex, id=section_id,
                                                   own_offset=section_offset_value, name=section_name)
            elif section_data_type == SectionType.FF8_TEXT:

                new_section = FF8SectionText(game_data=self.game_data, id=section_id, own_offset=section_offset_value,
                                             data_hex=section_data_hex,
                                             section_data_linked=None,
                                             name=section_name)
            elif section_data_type == SectionType.TKMNMES:
                new_section = SectionTkmnmesManager(game_data=self.game_data, id=section_id, own_offset=section_offset_value,
                                                    data_hex=section_data_hex,
                                                    name=section_name)
            elif section_data_type == SectionType.MNGRP_MAP_COMPLEX_STRING:
                map_complex_string = SectionMapComplexString(game_data=self.game_data, id=section_id, own_offset=section_offset_value,
                                                             data_hex=section_data_hex,
                                                             name=section_name)
                self.section_complex_string.add_map_section(map_complex_string)
                new_section = None
            elif section_data_type == SectionType.MNGRP_COMPLEX_STRING:
                new_section = SectionComplexStringEntry(game_data=self.game_data, id=section_id, own_offset=section_offset_value,
                                                        data_hex=section_data_hex,
                                                        name=section_name)
                self.section_complex_string.add_string_entry(new_section)
            elif section_data_type == SectionType.MNGRP_M00BIN:
                new_section = Sectionm00Bin(game_data=self.game_data, id=section_id, own_offset=section_offset_value,
                                            data_hex=section_data_hex,
                                            name=section_name, m00_id=m00bin_counter)
                m00bin_counter += 1

            elif section_data_type == SectionType.MNGRP_M00MSG:
                new_section = FF8SectionText(game_data=self.game_data, id=section_id, own_offset=section_offset_value,
                                             data_hex=section_data_hex,
                                             name=section_name)
                for section in self.mngrp.get_section_list():
                    if section.type == SectionType.MNGRP_M00BIN and section.m00_id == m00msg_counter:
                        section.section_data_linked = section
                        section.section_data_linked.section_text_linked = new_section
                        new_section.init_text(section.get_all_offset())
                        break

                m00msg_counter += 1

            else:  # Just saving the data, but will not be modified
                new_section = None # No need to create a new section
                # new_section.init_subsection(nb_subsection=entry_info['number_sub_section'], subsection_sized=entry_info['sub_section_size'])
            if new_section:
                self.mngrp.set_section_by_id(section_id, new_section, self.mngrphd)

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
