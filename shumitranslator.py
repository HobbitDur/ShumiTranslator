import csv
import os
import pathlib

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QScrollArea, QPushButton, QFileDialog, QHBoxLayout, QLabel, \
    QMessageBox

from FF8GameData.gamedata import GameData
from kernel.kernelsectiondata import KernelSectionData
from kernel.kernelsectionheader import KernelSectionHeader
from kernel.kernelsectiontext import KernelSectionText
from sectionwidget import SectionWidget


class ShumiTranslator(QWidget):
    CSV_FOLDER = "csv"

    def __init__(self, icon_path='Resources'):
        QWidget.__init__(self)

        # Special data
        self.game_data = GameData("FF8GameData")
        self.game_data.load_kernel_data()
        self.current_file_data = bytearray()
        self.translation_list = []
        self.file_loaded = ""
        self.csv_loaded = ""

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
        self.setMinimumSize(1080, 720)
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

        self.text_file_loaded = QLabel("File loaded: None")
        self.text_file_loaded.hide()
        self.layout_top = QHBoxLayout()
        self.layout_top.addWidget(self.file_dialog_button)
        self.layout_top.addWidget(self.save_button)
        self.layout_top.addWidget(self.csv_save_button)
        self.layout_top.addWidget(self.csv_upload_button)
        self.layout_top.addSpacing(20)
        self.layout_top.addWidget(self.text_file_loaded)
        self.layout_top.addStretch(1)

        # Warning
        self.warning_label_widget = QLabel(
            "<b>WARNING:</b> Don't modify {x0...}, {HP} and {GF} text as they are variable for the game")
        self.layout_full_top = QVBoxLayout()
        self.layout_full_top.addLayout(self.layout_top)
        self.layout_full_top.addWidget(self.warning_label_widget)

        # Translation management
        self.section_widget_list = []
        self.section_list = []
        self.layout_translation_lines = QVBoxLayout()

        # Main management
        self.window_layout.addLayout(self.layout_full_top)

        self.layout_main.addLayout(self.layout_translation_lines)

        self.window_layout.addWidget(self.scroll_area)

    def __save_file(self):
        self.save_button.setDown(True)
        self.scroll_area.setEnabled(False)
        if self.file_loaded:
            current_offset = 0
            self.current_file_data = bytearray()

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
                self.current_file_data.extend(section.get_data_hex())
            with open(self.file_loaded, "wb") as in_file:
                in_file.write(self.current_file_data)
            print("File saved")

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
                    self.csv_loaded = csv_to_load

                    with open(self.csv_loaded, newline='', encoding="utf-8") as csv_file:

                        csv_data = csv.reader(csv_file, delimiter=';', quotechar='|')
                        row_index = 1
                        csv_data_list = []
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
                            if text_loaded != "":  # If empty it will not be applied, so better be fast
                                for widget_index, widget in enumerate(self.section_widget_list):
                                    if widget.section.type == "text" and widget.section.id == section_text_id:
                                        self.section_widget_list[widget_index].set_text_from_id(text_id, text_loaded)
                    print("csv loaded")
                except UnicodeDecodeError:
                    message_box = QMessageBox()
                    message_box.setText("Wrong <b>encoding</b>, please use <b>UTF8</b> formating only")
                    message_box.setIcon(QMessageBox.Icon.Critical)
                    message_box.setWindowTitle("ShumiTranslator - Wrong CSV encoding")
                    message_box.setWindowIcon(self.__shumi_icon)
                    message_box.exec()


                self.scroll_area.setEnabled(True)

    def __save_csv(self):
        self.scroll_area.setEnabled(False)
        if self.file_loaded:
            os.makedirs(self.CSV_FOLDER, exist_ok=True)
            csv_name = pathlib.Path(self.file_loaded).name
            csv_name = csv_name.split('.')[0] + '.csv'
            default_file_name = os.path.join(self.CSV_FOLDER, csv_name)
            file_to_save = self.csv_save_dialog.getSaveFileName(parent=self, caption="Find csv file", filter="*.csv",
                                                                directory=default_file_name)[0]
            if file_to_save:
                with open(file_to_save, 'w', newline='', encoding="utf-8") as csv_file:
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

                print("Csv saved")
                self.scroll_area.setEnabled(True)

    def __load_file(self, file_to_load: str = ""):
        self.scroll_area.setEnabled(False)
        # file_to_load = os.path.join("OriginalFiles", "kernel.bin")  # For developing faster
        if not file_to_load:
            file_to_load = self.file_dialog.getOpenFileName(parent=self, caption="Find file", filter="*",
                                                            directory=os.getcwd())[0]

        if file_to_load:
            self.file_loaded = file_to_load
            self.csv_save_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.csv_upload_button.setEnabled(True)

            self.text_file_loaded.setText("File loaded: " + pathlib.Path(self.file_loaded).name)

            for section_widget in self.section_widget_list:
                section_widget.setParent(None)
                section_widget.deleteLater()
            self.section_widget_list = []
            self.current_file_data = bytearray()
            with open(self.file_loaded, "rb") as in_file:
                while el := in_file.read(1):
                    self.current_file_data.extend(el)
            self.__load_text_from_file()
            self.text_file_loaded.show()

        self.scroll_area.setEnabled(True)

    def __load_text_from_file(self):
        # First we read all offset section
        self.section_list = []
        # +1 for the number of section
        section_header = KernelSectionHeader(game_data=self.game_data, data_hex=self.current_file_data[0:(len(
            self.game_data.kernel_data_json["sections"]) + 1) * KernelSectionHeader.OFFSET_SIZE], name="header")
        self.section_list.append(section_header)
        for id, section_info in enumerate(self.game_data.kernel_data_json["sections"]):
            section_id = id + 1
            section_offset_value = self.section_list[0].get_section_offset_value_from_id(section_id)
            next_section_offset_value = self.section_list[0].get_section_offset_value_from_id(section_id + 1)
            own_offset = section_offset_value
            if next_section_offset_value is None:
                next_section_offset_value = len(self.current_file_data)
            if section_info["type"] == "data":
                new_section = KernelSectionData(game_data=self.game_data, id=section_id, own_offset=own_offset,
                                                data_hex=self.current_file_data[own_offset:next_section_offset_value],
                                                subsection_nb_text_offset=section_info['sub_section_nb_text_offset'],
                                                name=section_info['section_name'])
                new_section.init_subsection(nb_subsection=section_info['number_sub_section'],
                                            subsection_sized=section_info['sub_section_size'])
            elif section_info["type"] == "text":
                section_data_linked = [self.section_list[i] for i in range(1, len(self.section_list)) if
                                       section_info['section_offset_data_linked'] == self.section_list[
                                           0].get_section_header_offset_from_id(i)][0]
                new_section = KernelSectionText(game_data=self.game_data, id=section_id, own_offset=own_offset,
                                                data_hex=self.current_file_data[own_offset:next_section_offset_value],
                                                section_data_linked=section_data_linked,
                                                name=section_info['section_name'])
            else:
                new_section = None
                # new_section.init_subsection(nb_subsection=section_info['number_sub_section'], subsection_sized=section_info['sub_section_size'])
            self.section_list.append(new_section)

        for i, section in enumerate(self.section_list):
            if section.type == "text":
                # Adding the link from data to text as text were not constructed yet.
                section.section_data_linked.section_text_linked = section
                # Initializing the text now that we can get all the offset
                all_offset = section.section_data_linked.get_all_offset()
                section.init_text(all_offset)
                self.section_widget_list.append(SectionWidget(section))
                self.layout_translation_lines.addWidget(self.section_widget_list[-1])
