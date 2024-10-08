from FF8GameData.FF8HexReader.mngrp import Mngrp
from FF8GameData.FF8HexReader.mngrphd import Mngrphd
from mngrp.m00x.m00xmanager import m00XManager
from mngrp.textbox.sectiontextboxentry import SectionTextBoxEntry
from mngrp.textbox.textboxmanager import TextBoxManager
from mngrp.textbox.sectionmaptextbox import SectionMapTextBox
from mngrp.m00x.sectionm00bin import Sectionm00Bin
from mngrp.string.sectionstring import SectionString
import csv

from FF8GameData.gamedata import GameData, SectionType
from general.ff8sectiontext import FF8SectionText
from mngrp.tkmnmes.sectiontkmnmes import SectionTkmnmes


class MngrpManager:
    def __init__(self, game_data: GameData):

        self.mngrphd = None
        self.mngrp = None
        self.game_data = game_data
        self.text_box_manager = TextBoxManager()
        self.m00_manager = m00XManager()

    def __str__(self):
        return str(self.mngrp)

    def __repr__(self):
        return self.__str__()

    def save_file(self, file_mngrp, file_mngrphd):

        # Some sections are interdependent, so we update their value first
        self.text_box_manager.update_map_offset()
        self.m00_manager.update_offset()

        # then we update mngrp hex
        self.mngrp.update_data_hex()

        # Updating mngrphd value from ther new mngrp computed
        self.mngrphd.update_from_section_list(self.mngrp.get_section_list())
        self.mngrphd.update_data_hex()

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
            if self.mngrphd.get_entry_list()[index].invalid_value:  # If it's a non-existent section, ignore it
                continue
            section_id = section_mngrp.id
            section_data_type = self.game_data.mngrp_data_json["sections"][section_id]["data_type"]
            section_name = self.game_data.mngrp_data_json["sections"][section_id]["section_name"]
            section_offset_value = section_mngrp.own_offset
            section_data_hex = section_mngrp.get_data_hex()
            if section_data_type == SectionType.MNGRP_STRING:
                new_section = SectionString(game_data=self.game_data, data_hex=section_data_hex, id=section_id,
                                            own_offset=section_offset_value, name=section_name)
            elif section_data_type == SectionType.FF8_TEXT:
                new_section = FF8SectionText(game_data=self.game_data, id=section_id, own_offset=section_offset_value,
                                             data_hex=section_data_hex,
                                             section_data_linked=None,
                                             name=section_name)
            elif section_data_type == SectionType.TKMNMES:
                new_section = SectionTkmnmes(game_data=self.game_data, id=section_id, own_offset=section_offset_value,
                                             data_hex=section_data_hex,
                                             name=section_name)
            elif section_data_type == SectionType.MNGRP_MAP_COMPLEX_STRING:
                map_complex_string = SectionMapTextBox(game_data=self.game_data, id=section_id,
                                                       own_offset=section_offset_value,
                                                       data_hex=section_data_hex,
                                                       name=section_name)
                self.text_box_manager.add_map_section(map_complex_string)
                new_section = map_complex_string
            elif section_data_type == SectionType.MNGRP_TEXTBOX:
                new_section = SectionTextBoxEntry(game_data=self.game_data, id=section_id,
                                                  own_offset=section_offset_value,
                                                  data_hex=section_data_hex,
                                                  name=section_name)
                self.text_box_manager.add_string_entry(new_section)
            elif section_data_type == SectionType.MNGRP_M00BIN:
                new_section = Sectionm00Bin(game_data=self.game_data, id=section_id, own_offset=section_offset_value,
                                            data_hex=section_data_hex,
                                            name=section_name, m00_id=m00bin_counter)
                self.m00_manager.add_bin(new_section)
                m00bin_counter += 1
            elif section_data_type == SectionType.MNGRP_M00MSG:
                new_section = FF8SectionText(game_data=self.game_data, id=section_id, own_offset=section_offset_value,
                                             data_hex=section_data_hex,
                                             name=section_name)
                new_section.type = SectionType.MNGRP_M00MSG
                self.m00_manager.add_msg(new_section)
                for section in self.mngrp.get_section_list():
                    if section.type == SectionType.MNGRP_M00BIN and section.m00_id == m00msg_counter:
                        section.section_data_linked = section
                        section.section_data_linked.section_text_linked = new_section
                        new_section.init_text(section.get_all_offset())
                        break
                m00msg_counter += 1

            else:  # Just saving the data, but will not be modified
                new_section = None  # No need to create a new section
            if new_section:
                self.mngrp.set_section_by_id(section_id, new_section)

    def save_csv(self, csv_path):
        if csv_path:
            with open(csv_path, 'w', newline='', encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(
                    ['Section data name', 'Section id', 'Subsection id', 'Text Sub id', 'Text'])
                text_line = 2
                for index_section, section in enumerate(self.mngrp.get_section_list()):
                    if section.type in (
                            SectionType.TKMNMES, SectionType.MNGRP_STRING, SectionType.FF8_TEXT,
                            SectionType.MNGRP_TEXTBOX, SectionType.MNGRP_M00MSG):
                        if section.type == SectionType.TKMNMES:
                            for i in range(section.get_nb_text_section()):
                                text_section = section.get_text_section_by_id(i)
                                subsection_id = text_section.id
                                for ff8text in text_section.get_text_list():
                                    csv_writer.writerow(
                                        [section.name, section.id, subsection_id, ff8text.id,  ff8text.get_str()])
                                    text_line += 1
                        if section.type == SectionType.MNGRP_TEXTBOX:
                            for i in range(section.get_nb_entry_section()):
                                entry_section = section.get_entry_section_by_id(i)
                                subsection_id = entry_section.id
                                for ff8text in entry_section.get_text_list():
                                    csv_writer.writerow(
                                        [section.name, section.id, subsection_id, ff8text.id,  ff8text.get_str()])
                                    text_line += 1
                        if section.type in (SectionType.MNGRP_M00MSG, SectionType.FF8_TEXT, SectionType.MNGRP_STRING):
                                for ff8text in section.get_text_list():
                                    csv_writer.writerow(
                                        [section.name, section.id, 0, ff8text.id,  ff8text.get_str()])
                                    text_line += 1


    def load_csv(self, csv_to_load, section_widget_list):
        if csv_to_load:
            with open(csv_to_load, newline='', encoding="utf-8") as csv_file:

                csv_data = csv.reader(csv_file, delimiter=';', quotechar='|')
                #   ['Section data name', 'Section id', 'Subsection id', 'Text Sub id', 'Text']
                tkmnmes_index =0
                for row_index, row in enumerate(csv_data):
                    if row_index == 0:  # Ignoring title row
                        continue

                    #section_data_name = row[0]
                    section_id = int(row[1])
                    subsection_id = int(row[2])
                    text_sub_id = int(row[3])
                    text_loaded = row[4]

                    if text_loaded == "":
                        continue
                    # Managing this case as many people do the mistake.
                    text_loaded = text_loaded.replace('`', "'")
                    for widget_index, widget in enumerate(section_widget_list):
                        if widget.section.type in (
                                SectionType.TKMNMES, SectionType.MNGRP_STRING, SectionType.FF8_TEXT,
                                SectionType.MNGRP_TEXTBOX, SectionType.MNGRP_M00MSG):
                            if widget.section.id == section_id:
                                if widget.section.type == SectionType.MNGRP_TEXTBOX:
                                    nb_sub_element = 0
                                    for i in range(widget.section.get_nb_entry_section()):
                                        entry_section = widget.section.get_entry_section_by_id(i)
                                        if entry_section.id < subsection_id :
                                            nb_sub_element += len(entry_section.get_text_list())
                                        elif subsection_id == entry_section.id:
                                            nb_sub_element += text_sub_id
                                            text_sub_id = nb_sub_element
                                            break
                                        elif entry_section.id > subsection_id :
                                            print(
                                                f"In csv, unexpected error where subsection id ({subsection_id})> entry_section id ({entry_section.id})")
                                elif widget.section.type == SectionType.TKMNMES:

                                    nb_sub_element = 0
                                    for i in range(widget.section.get_nb_text_section()):
                                        text_section = widget.section.get_text_section_by_id(i)
                                        if text_section.id < subsection_id:
                                            nb_sub_element += len(text_section.get_text_list())
                                        elif subsection_id == text_section.id:
                                            nb_sub_element += text_sub_id
                                            text_sub_id = nb_sub_element
                                            break
                                        elif text_section.id > subsection_id:
                                            print(f"In csv, unexpected error where subsection id ({subsection_id})> text_section id ({text_section.id})")



                                section_widget_list[widget_index].set_text_from_id(text_sub_id, text_loaded)
                                break
