from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QLabel, QVBoxLayout

from gamedata import GameData
from subsection import SubSection
from translationwidget import TranslationWidget


class SubSectionWidget(QWidget):

    def __init__(self, sub_section: SubSection):
        QWidget.__init__(self)

        self.sub_section = sub_section
        self.__sub_section_name_widget = QLabel()
        self.__sub_section_name_widget.setText("<u>Sub section n°" + str(self.sub_section.sub_section_id) + "</u>")

        self.__title_layout = QHBoxLayout()
        self.__title_layout.addSpacing(10)
        self.__title_layout.addWidget(self.__sub_section_name_widget)


        self.translation_widget_list = []

        self.__main_layout = QVBoxLayout()
        self.__main_layout.addLayout(self.__title_layout)

        self.setLayout(self.__main_layout)
        self.__create_translation_widget()

    def __create_translation_widget(self):
        for translation in self.sub_section.translation_list:
            translation_widget = TranslationWidget(translation)
            self.translation_widget_list.append(translation_widget)
            self.__main_layout.addWidget(self.translation_widget_list[-1])
