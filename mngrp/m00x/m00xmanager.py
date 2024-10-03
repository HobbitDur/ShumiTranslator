from FF8GameData.FF8HexReader.section import Section
from FF8GameData.gamedata import GameData, SectionType
from general.ff8sectiontext import FF8SectionText
from mngrp.m00x.sectionm00bin import Sectionm00Bin
from mngrp.textbox.textboxentry import TextBoxEntry
from mngrp.textbox.sectiontextboxentry import SectionTextBoxEntry
from mngrp.textbox.sectionmaptextbox import SectionMapTextBox


class m00XManager:

    def __init__(self):
        self._m00bin_list = []
        self._m00msg_list = []
        self.type = SectionType.DATA

    def add_bin(self, bin_section: Sectionm00Bin):
        self._m00bin_list.append(bin_section)

    def add_msg(self, msg_section: FF8SectionText):
        self._m00msg_list.append(msg_section)

    def update_offset(self):
        for i in range(len(self._m00bin_list)):
            self._m00bin_list[i].set_offset_by_text_list(self._m00msg_list[i].get_text_list())
