from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QFrame

from kernel.kernelsectiontext import KernelSectionText
from translationwidget import TranslationWidget


class SectionWidget(QWidget):

    def __init__(self, section: KernelSectionText, first_section_line_index):
        QWidget.__init__(self)

        self.section = section
        self.first_section_line_index = first_section_line_index
        self.__section_name_widget = QLabel()
        self.__section_name_widget.setText(f"<b><u>Section text n°{self.section.id}:</u></b> " + self.section.name)

        self.translation_widget_list = []

        self.__main_layout = QVBoxLayout()
        self.__main_layout.addWidget(self.__section_name_widget)

        self.setLayout(self.__main_layout)
        self.__create_sub_section_widget()

    def __str__(self):
        return "Widget " + str(self.section)

    def __create_sub_section_widget(self):
        for i, kernel_text in enumerate(self.section.get_text_list()):
            translation_widget = TranslationWidget(kernel_text, self.first_section_line_index + i)
            self.translation_widget_list.append(translation_widget)
            self.__main_layout.addWidget(self.translation_widget_list[-1])
        end_separator_line = QFrame()
        end_separator_line.setFrameStyle(0x04)# Horizontal line
        end_separator_line.setLineWidth(2)
        self.__main_layout.addWidget(end_separator_line)

    def set_text_from_id(self, id: int, text: str):
        self.translation_widget_list[id].change_custom_text(text)
