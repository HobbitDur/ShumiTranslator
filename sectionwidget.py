from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout

from kernel.kernelsectiontext import KernelSectionText
from translationwidget import TranslationWidget


class SectionWidget(QWidget):

    def __init__(self, section: KernelSectionText):
        QWidget.__init__(self)

        self.section = section
        self.__section_name_widget = QLabel()
        self.__section_name_widget.setText("<u><b>Section: </u></b>" + self.section.name)

        self.translation_widget_list = []

        self.__main_layout = QVBoxLayout()
        self.__main_layout.addWidget(self.__section_name_widget)

        self.setLayout(self.__main_layout)
        self.__create_sub_section_widget()

    def __str__(self):
        return "Widget " + str(self.section)

    def __create_sub_section_widget(self):
        for kernel_text in self.section.get_text_list():
            translation_widget = TranslationWidget(kernel_text)
            self.translation_widget_list.append(translation_widget)
            self.__main_layout.addWidget(self.translation_widget_list[-1])

    def set_text_from_id(self, id: int, text: str):
        self.translation_widget_list[id].change_custom_text(text)
