from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout

from gamedata import GameData
from section import Section
from subsectionwidget import SubSectionWidget
from translationwidget import TranslationWidget


class SectionWidget(QWidget):

    def __init__(self, section:Section):
        QWidget.__init__(self)

        self.section = section
        self.__section_name_widget = QLabel()
        self.__section_name_widget.setText("<u><b>Section: </u></b>" + self.section.section_name)

        self.sub_section_widget_list = []

        self.__main_layout = QVBoxLayout()
        self.__main_layout.addWidget(self.__section_name_widget)

        self.setLayout(self.__main_layout)
        self.__create_sub_section_widget()
        if not self.section.sub_section_sub_offset:
            self.hide()

    def __create_sub_section_widget(self):
        for subsection in self.section.subsection_list:
            sub_section_widget = SubSectionWidget(subsection)
            self.sub_section_widget_list.append(sub_section_widget)
            self.__main_layout.addWidget(self.sub_section_widget_list[-1])
