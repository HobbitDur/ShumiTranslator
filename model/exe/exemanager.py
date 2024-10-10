from FF8GameData.ExeSection.exefile import SectionExeFile
from FF8GameData.FF8HexReader.mngrp import Mngrp
from FF8GameData.FF8HexReader.mngrphd import Mngrphd
from model.mngrp.m00x.m00xmanager import m00XManager
from model.mngrp.textbox.sectiontextboxentry import SectionTextBoxEntry
from model.mngrp.textbox.textboxmanager import TextBoxManager
from model.mngrp.textbox.sectionmaptextbox import SectionMapTextBox
from model.mngrp.m00x.sectionm00bin import Sectionm00Bin
from model.mngrp.string.sectionstring import SectionString
import csv

from FF8GameData.gamedata import GameData, SectionType
from FF8GameData.GenericSection.listff8text import ListFF8Text
from model.mngrp.tkmnmes.sectiontkmnmes import SectionTkmnmes


class ExeManager:
    def __init__(self, game_data: GameData):
        self.game_data = game_data
        self.exe_section = None

    def __str__(self):
        return str(self.exe_section)

    def __repr__(self):
        return self.__str__()

    def get_exe_section(self) -> SectionExeFile:
        return self.exe_section

    def save_file(self, hext_file):
        with open(hext_file, "w") as hext_file:
            hext_file.write(self.exe_section.produce_str_hext(card_name=True))


    def load_file(self, file_exe):
        exe_hex = bytearray()
        with open(file_exe, "rb") as file:
            exe_hex.extend(file.read())

        self.exe_section = SectionExeFile(self.game_data, exe_hex)

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
