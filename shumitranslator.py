import os
import pathlib

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QScrollArea, QPushButton, QFileDialog, QHBoxLayout, QLabel, \
    QMessageBox

from FF8GameData.gamedata import GameData, FileType, SectionType
from kernel.kernelmanager import KernelManager
from mngrp.complexstring.sectioncomplexstringmanager import SectionComplexStringManager
from mngrp.complexstring.sectionmapcomplexstring import SectionMapComplexString
from mngrp.mngrpmanager import MngrpManager
from mngrp.string.sectionstringmanager import SectionStringManager
from sectionwidget import SectionWidget


class ShumiTranslator(QWidget):
    CSV_FOLDER = "csv"
    FILE_MANAGED = ['kernel.bin', 'namedic.bin', 'mngrp.bin']
    FILE_MANAGED_REGEX = ['*kernel*.bin', '*namedic*.bin', '*mngrp*.bin']

    def __init__(self, icon_path='Resources'):
        QWidget.__init__(self)

        # Special data
        self.game_data = GameData("FF8GameData")
        self.game_data.load_kernel_data()
        self.game_data.load_mngrp_data()
        self.translation_list = []
        self.file_loaded = ""
        self.csv_loaded = ""
        self.file_loaded_type = FileType.NONE

        # Window management
        self.window_layout = QVBoxLayout()
        self.setLayout(self.window_layout)
        self.scroll_widget = QWidget()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        self.layout_main = QVBoxLayout()
        self.scroll_widget.setLayout(self.layout_main)

        self.setWindowTitle("ShumiTranslator")
        self.setMinimumSize(800, 800)
        self.__shumi_icon = QIcon(os.path.join(icon_path, 'icon.ico'))
        self.setWindowIcon(self.__shumi_icon)

        # Top management
        self.file_dialog = QFileDialog()
        self.file_dialog_button = QPushButton()
        self.file_dialog_button.setIcon(QIcon(os.path.join(icon_path, 'folder.png')))
        self.file_dialog_button.setIconSize(QSize(30, 30))
        self.file_dialog_button.setFixedSize(40, 40)
        self.file_dialog_button.setToolTip("Open data file")
        self.file_dialog_button.clicked.connect(self.__load_file)

        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon(os.path.join(icon_path, 'save.svg')))
        self.save_button.setIconSize(QSize(30, 30))
        self.save_button.setFixedSize(40, 40)
        self.save_button.setToolTip("Save to file")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.__save_file)

        self.csv_save_dialog = QFileDialog()
        self.csv_save_button = QPushButton()
        self.csv_save_button.setIcon(QIcon(os.path.join(icon_path, 'csv_save.png')))
        self.csv_save_button.setIconSize(QSize(30, 30))
        self.csv_save_button.setFixedSize(40, 40)
        self.csv_save_button.setToolTip("Save to csv")
        self.csv_save_button.setEnabled(False)
        self.csv_save_button.clicked.connect(self.__save_csv)

        self.csv_upload_button = QPushButton()
        self.csv_upload_button.setIcon(QIcon(os.path.join(icon_path, 'csv_upload.png')))
        self.csv_upload_button.setIconSize(QSize(30, 30))
        self.csv_upload_button.setFixedSize(40, 40)
        self.csv_upload_button.setToolTip("Upload csv")
        self.csv_upload_button.setEnabled(False)
        self.csv_upload_button.clicked.connect(self.__open_csv)

        self.compress_button = QPushButton()
        self.compress_button.setIcon(QIcon(os.path.join(icon_path, 'compress.png')))
        self.compress_button.setIconSize(QSize(30, 30))
        self.compress_button.setFixedSize(40, 40)
        self.compress_button.setToolTip("Compress data")
        self.compress_button.setEnabled(False)
        self.compress_button.clicked.connect(self.__compress_data)

        self.uncompress_button = QPushButton()
        self.uncompress_button.setIcon(QIcon(os.path.join(icon_path, 'uncompress.png')))
        self.uncompress_button.setIconSize(QSize(30, 30))
        self.uncompress_button.setFixedSize(40, 40)
        self.uncompress_button.setToolTip("Uncompress data")
        self.uncompress_button.setEnabled(False)
        self.uncompress_button.clicked.connect(self.__uncompress_data)

        self.info_button = QPushButton()
        self.info_button.setIcon(QIcon(os.path.join(icon_path, 'info.png')))
        self.info_button.setIconSize(QSize(30, 30))
        self.info_button.setFixedSize(40, 40)
        self.info_button.setToolTip("Show toolmaker info")
        self.info_button.clicked.connect(self.__show_info)

        self.text_file_loaded = QLabel("File loaded: None")
        self.text_file_loaded.hide()
        self.layout_top = QHBoxLayout()
        self.layout_top.addWidget(self.file_dialog_button)
        self.layout_top.addWidget(self.save_button)
        self.layout_top.addWidget(self.csv_save_button)
        self.layout_top.addWidget(self.csv_upload_button)
        self.layout_top.addWidget(self.compress_button)
        self.layout_top.addWidget(self.uncompress_button)
        self.layout_top.addWidget(self.info_button)
        self.layout_top.addSpacing(20)
        self.layout_top.addWidget(self.text_file_loaded)
        self.layout_top.addStretch(1)

        # Warning
        self.warning_kernel_label_widget = QLabel(
            "{x0...} are yet unknown text correspondence. Pls don't modify them.<br/>"
            "Value between {} are \"compressed\" data. Pls don't remove bracket around.<br/>"
            "The file as a size max (40456?).<br/>"
            "If you wish to get rid of parenthesis you can uncompress<br/>"
            "But pls compress before saving to avoid size problem.")
        self.warning_kernel_label_widget.hide()
        # Warning
        self.warning_mngrp_label_widget = QLabel(
            "{x0...} are yet unknown text correspondence. Pls don't modify them.<br/>"
            "Value between {} are \"compressed\" data. Pls don't remove bracket around.<br/>"
            "Value {x0a..} as often weird character after. Pls don't modify them<br/>")
        self.warning_mngrp_label_widget.hide()

        self.layout_full_top = QVBoxLayout()
        self.layout_full_top.addLayout(self.layout_top)
        # self.layout_full_top.addWidget(self.warning_label_widget)

        # Translation management
        self.section_list = []

        self.section_widget_list = []
        self.layout_translation_lines = QVBoxLayout()

        # Main management
        self.window_layout.addLayout(self.layout_full_top)
        self.layout_main.addWidget(self.warning_kernel_label_widget)
        self.layout_main.addWidget(self.warning_mngrp_label_widget)
        self.layout_main.addStretch(1)
        self.layout_main.addLayout(self.layout_translation_lines)

        self.window_layout.addWidget(self.scroll_area)

        self.kernel_manager = KernelManager(game_data=self.game_data)
        self.namedic_manager = SectionStringManager(game_data=self.game_data)
        self.mngrp_manager = MngrpManager(game_data=self.game_data)

    def __show_info(self):
        message_box = QMessageBox()
        message_box.setText(f"Tool done by <b>Hobbitdur</b>.<br/>"
                            f"You can support me on <a href='https://www.patreon.com/HobbitMods'>Patreon</a>.<br/>"
                            f"Special thanks to :<br/>"
                            f"&nbsp;&nbsp;-<b>Riccardo</b> for beta testing.<br/>"
                            f"&nbsp;&nbsp;-<b>myst6re</b> for all the retro-engineering.")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowIcon(self.__shumi_icon)
        message_box.setWindowTitle("ShumiTranslator - Info")
        message_box.exec()

    def __compress_data(self):
        # Not all data can be compressed, so we do case by case
        # We give to the subsection the offset that can be compressed (0=None, 1=First, 2 = Second, 3=Both)
        self.scroll_area.setEnabled(False)
        for index_section, section_widget in enumerate(self.section_widget_list):
            compressibility_factor = \
                [x["compressibility_factor"] for x in self.game_data.kernel_data_json["sections"] if
                 x["id"] == section_widget.section.id][
                    0]
            section_widget.compress_str(compressibility_factor)
        self.scroll_area.setEnabled(True)

    def __uncompress_data(self):
        self.scroll_area.setEnabled(False)
        for index_section, section_widget in enumerate(self.section_widget_list):
            section_widget.uncompress_str()
        self.scroll_area.setEnabled(True)

    def __save_file(self):
        self.save_button.setDown(True)
        self.scroll_area.setEnabled(False)
        if self.file_loaded:
            if self.file_loaded_type == FileType.KERNEL:
                self.kernel_manager.save_file(self.file_loaded)
            elif self.file_loaded_type == FileType.NAMEDIC:
                self.namedic_manager.save_file(self.file_loaded)

        message_box = QMessageBox()
        message_box.setText("Data saved to file <b>{}</b>".format(pathlib.Path(self.file_loaded).name))
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle("ShumiTranslator - Data saved")
        message_box.setWindowIcon(self.__shumi_icon)
        message_box.exec()
        self.save_button.setDown(False)
        self.scroll_area.setEnabled(True)

    def __open_csv(self, csv_to_load: str = ""):
        self.scroll_area.setEnabled(False)
        if self.file_loaded:
            if not csv_to_load:
                if os.path.isdir(self.CSV_FOLDER):
                    directory = self.CSV_FOLDER
                else:
                    directory = os.getcwd()
                csv_to_load = \
                    self.csv_save_dialog.getOpenFileName(parent=self, caption="Find csv file (in UTF8 format only)",
                                                         filter="*.csv", directory=directory)[0]
            if csv_to_load:
                try:
                    if self.file_loaded_type == FileType.KERNEL:
                        self.kernel_manager.load_csv(csv_to_load=csv_to_load, section_widget_list=self.section_widget_list)
                    elif self.file_loaded_type == FileType.NAMEDIC:
                        self.namedic_manager.load_csv(csv_to_load=csv_to_load, section_widget_list=self.section_widget_list)
                except UnicodeDecodeError as e:
                    print(e)
                    message_box = QMessageBox()
                    message_box.setText("Wrong <b>encoding</b>, please use <b>UTF8</b> formating only.<br>"
                                        "In excel, you can go to the \"Data tab\", \"Import text file\" and choose UTF8 encoding")
                    message_box.setIcon(QMessageBox.Icon.Critical)
                    message_box.setWindowTitle("ShumiTranslator - Wrong CSV encoding")
                    message_box.setWindowIcon(self.__shumi_icon)
                    message_box.exec()

        self.scroll_area.setEnabled(True)

    def __save_csv(self):
        os.makedirs(self.CSV_FOLDER, exist_ok=True)
        csv_name = pathlib.Path(self.file_loaded).name
        csv_name = csv_name.split('.')[0] + '.csv'
        default_file_name = os.path.join(self.CSV_FOLDER, csv_name)
        file_to_save = self.csv_save_dialog.getSaveFileName(parent=self, caption="Find csv file", filter="*.csv",
                                                            directory=default_file_name)[0]
        if self.file_loaded_type == FileType.KERNEL:
            self.kernel_manager.save_csv(file_to_save)
        elif self.file_loaded_type == FileType.NAMEDIC:
            self.namedic_manager.save_csv(file_to_save)

    def __load_file(self, file_to_load: str = ""):
        print("Loading file")

        self.scroll_area.setEnabled(False)
        self.compress_button.setEnabled(False)
        self.uncompress_button.setEnabled(False)
        self.compress_button.hide()
        self.uncompress_button.hide()
        self.warning_kernel_label_widget.hide()
        self.warning_mngrp_label_widget.hide()
        file_to_load = os.path.join("OriginalFiles", "mngrp.bin")  # For developing faster
        if not file_to_load:
            filter_txt = ""
            for file_regex in self.FILE_MANAGED_REGEX:
                filter_txt += file_regex
                filter_txt += ";"

            file_to_load = self.file_dialog.getOpenFileName(parent=self, caption="Find file", filter=filter_txt,
                                                            directory=os.getcwd())[0]

        if file_to_load:
            self.file_dialog_button.setEnabled(False)
            self.file_loaded = file_to_load
            file_name = pathlib.Path(self.file_loaded).name
            self.text_file_loaded.setText("File loaded: " + file_name)

            for section_widget in self.section_widget_list:
                section_widget.setParent(None)
                section_widget.deleteLater()
            self.section_widget_list = []

            # Choose which manager to load
            if "kernel" in file_name and ".bin" in file_name:
                self.file_loaded_type = FileType.KERNEL
                self.kernel_manager.load_file(self.file_loaded)
                first_section_line_index = 2  # Start at 2 as in the CSV
                for section in self.kernel_manager.section_list:
                    if section.type == SectionType.FF8_TEXT:
                        self.section_widget_list.append(SectionWidget(section, first_section_line_index))
                        self.layout_translation_lines.addWidget(self.section_widget_list[-1])
                        first_section_line_index += len(section.section_data_linked.get_all_offset())
                self.compress_button.setEnabled(True)
                self.uncompress_button.setEnabled(True)
                self.compress_button.show()
                self.uncompress_button.show()
                self.warning_kernel_label_widget.show()


            elif "namedic" in file_name and ".bin" in file_name:
                self.file_loaded_type = FileType.NAMEDIC
                self.namedic_manager.load_file(self.file_loaded)
                # Only one section
                first_section_line_index = 2  # Start at 2 as in the CSV
                self.section_widget_list.append(SectionWidget(self.namedic_manager.get_text_section(), first_section_line_index))
                self.layout_translation_lines.addWidget(self.section_widget_list[-1])


            elif "mngrp" in file_name and ".bin" in file_name:
                self.file_loaded_type = FileType.MNGRP
                self.mngrp_manager.load_file(self.file_loaded)

                first_section_line_index = 2
                for section in self.mngrp_manager.section_list:
                    if section.type in [SectionType.MNGRP_STRING, SectionType.FF8_TEXT, SectionType.TKMNMES, SectionType.MNGRP_COMPLEX_STRING]:
                        if section.type == SectionType.MNGRP_STRING:
                            self.section_widget_list.append(SectionWidget(section.get_text_section(), first_section_line_index))
                            first_section_line_index += len(section.get_text_list())
                            self.layout_translation_lines.addWidget(self.section_widget_list[-1])
                        elif section.type == SectionType.FF8_TEXT:
                            self.section_widget_list.append(SectionWidget(section, first_section_line_index))
                            first_section_line_index += len(section.get_text_list())
                            self.layout_translation_lines.addWidget(self.section_widget_list[-1])
                        elif section.type == SectionType.TKMNMES:
                            for i in range(section.get_nb_text_section()):
                                self.section_widget_list.append(SectionWidget(section.get_text_section_by_id(i), first_section_line_index))
                                first_section_line_index += len(section.get_text_section_by_id(i).get_text_list())
                                self.layout_translation_lines.addWidget(self.section_widget_list[-1])
                        elif section.type == SectionType.MNGRP_COMPLEX_STRING:
                            self.section_widget_list.append(SectionWidget(section, first_section_line_index))
                            self.layout_translation_lines.addWidget(self.section_widget_list[-1])
                    self.warning_mngrp_label_widget.show()

            self.csv_save_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.csv_upload_button.setEnabled(True)
            self.file_dialog_button.setEnabled(True)
            self.text_file_loaded.show()

        self.scroll_area.setEnabled(True)

    def __disable_all(self):
        self.csv_save_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.csv_upload_button.setEnabled(False)
        self.compress_button.setEnabled(False)
        self.uncompress_button.setEnabled(False)
        self.scroll_area.setEnabled(False)

    def __enable_all(self):
        self.csv_save_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.csv_upload_button.setEnabled(True)
        self.compress_button.setEnabled(True)
        self.uncompress_button.setEnabled(True)
        self.scroll_area.setEnabled(True)
