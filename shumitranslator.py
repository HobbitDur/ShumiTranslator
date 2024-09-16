import csv
import os
import pathlib

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QScrollArea, QPushButton, QFileDialog, QComboBox, QHBoxLayout, QLabel, \
    QColorDialog, QCheckBox

from gamedata import GameData
from section import Section
from sectionwidget import SectionWidget
from translation import Translation
from translationwidget import TranslationWidget


class ShumiTranslator(QWidget):
    CSV_FOLDER = "csv"
    def __init__(self, icon_path='Resources'):
        QWidget.__init__(self)

        # Special data
        self.game_data = GameData()
        self.game_data.load_kernel_data(os.path.join("Resources", "kernel_bin_data.json"))
        self.current_file_data = bytearray()
        self.translation_list = []

        # Window management
        self.window_layout = QVBoxLayout()
        self.setLayout(self.window_layout)
        self.scroll_widget = QWidget()
        self.scroll_area = QScrollArea()
        self.window_layout.addWidget(self.scroll_area)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        self.layout_main = QVBoxLayout()
        self.scroll_widget.setLayout(self.layout_main)

        self.setWindowTitle("ShumiTranslator")
        self.setMinimumSize(1080, 720)
        self.setWindowIcon(QIcon(os.path.join(icon_path, 'icon.ico')))

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
        self.save_button.clicked.connect(self.__save_file)

        self.csv_save_dialog = QFileDialog()
        self.csv_save_button = QPushButton()
        self.csv_save_button.setIcon(QIcon(os.path.join(icon_path, 'csv_save.png')))
        self.csv_save_button.setIconSize(QSize(30, 30))
        self.csv_save_button.setFixedSize(40, 40)
        self.csv_save_button.setToolTip("Save to csv")
        self.csv_save_button.clicked.connect(self.__save_csv)

        self.csv_upload_button = QPushButton()
        self.csv_upload_button.setIcon(QIcon(os.path.join(icon_path, 'csv_upload.png')))
        self.csv_upload_button.setIconSize(QSize(30, 30))
        self.csv_upload_button.setFixedSize(40, 40)
        self.csv_upload_button.setToolTip("Upload csv")
        self.csv_upload_button.clicked.connect(self.__open_csv)

        self.text_file_loaded = QLabel("File loaded: None")

        self.layout_top = QHBoxLayout()
        self.layout_top.addWidget(self.file_dialog_button)
        self.layout_top.addWidget(self.save_button)
        self.layout_top.addWidget(self.csv_save_button)
        self.layout_top.addWidget(self.csv_upload_button)
        self.layout_top.addSpacing(20)
        self.layout_top.addWidget(self.text_file_loaded)
        self.layout_top.addStretch(1)

        # Translation management
        self.section_widget_list = []
        self.layout_translation_lines = QVBoxLayout()

        # Main management
        self.layout_main.addLayout(self.layout_top)
        self.layout_main.addLayout(self.layout_translation_lines)
        self.layout_main.addStretch(1)

        self.__load_file()

    def __save_file(self):
        added_offset = 0
        for section_widget in self.section_widget_list:
            section = section_widget.section
            print(f"section name: {section.section_name}")
            print(f"section offset value: {section.section_offset_value}")
            if added_offset != 0:
                section.section_offset_value += added_offset
                self.current_file_data[section.section_offset_address: section.section_offset_address+4] = section.section_offset_value.to_bytes(length=4, byteorder="little") #Flemme, +4 is the size
            for sub_section in section.subsection_list:
                added_sub_section_offset = 0
                print(f"sub_section id: {sub_section.sub_section_id}")
                for trans in sub_section.translation_list:
                    print(f"trans.offset_value: {trans.offset_value}")
                    print(f"trans.text_address: {trans.text_address}")
                    print(f"added_offset: {added_offset}")
                    print(f"added_sub_section_offset: {added_sub_section_offset}")
                    if trans.offset_value == 0xFFFF:# Means the data is not used
                        continue
                    custom_text_hex = self.game_data.translate_str_to_hex(trans.custom_text)
                    file_text_hex = self.game_data.translate_str_to_hex(trans.file_text)
                    if custom_text_hex == file_text_hex and added_offset == 0: # If no change at all, we can just go on with our life
                        continue
                    elif custom_text_hex != file_text_hex and len(custom_text_hex) == len(file_text_hex) and added_offset == 0: # Text changed but size same, don't care of offset
                        self.current_file_data[trans.text_address:trans.text_address + len(custom_text_hex)] = custom_text_hex
                        trans.file_text = trans.custom_text
                    else: # My life is a suffering
                        trans.offset_value += added_sub_section_offset
                        trans.offset_address += added_offset
                        trans.text_address += added_offset
                        added_sub_section_offset += len(custom_text_hex) - len(file_text_hex)
                        added_offset += len(custom_text_hex) - len(file_text_hex)
                        self.current_file_data[trans.offset_address:trans.offset_address + 2] = (trans.offset_value).to_bytes(length=2, byteorder="little")
                        del self.current_file_data[trans.text_address:trans.text_address + len(file_text_hex)]
                        trans.text_address += len(custom_text_hex) - len(file_text_hex)
                        for i in range(len(custom_text_hex)):
                            self.current_file_data.insert(trans.text_address + i, custom_text_hex[i])
                        trans.file_text = trans.custom_text



        print(f"Added offset {added_offset}")

        print("Saving file")
        with open(self.file_loaded, "wb") as in_file:
            in_file.write(self.current_file_data)
        print("File saved")

    def __open_csv(self, file_to_load: str = ""):
        #file_to_load = os.path.join("OriginalFiles", "kernel.bin")  # For developing faster
        #print(f"File to load: {file_to_load}")
        if not file_to_load:
            if os.path.isdir(self.CSV_FOLDER):
                directory = self.CSV_FOLDER
            else:
                directory = os.getcwd()
            file_to_load = self.csv_save_dialog.getOpenFileName(parent=self, caption="Find csv file", filter="*.csv",
                                                            directory=directory)[0]
        if file_to_load:
            self.file_loaded = file_to_load

            with open(self.file_loaded, newline='') as csv_file:

                csv_data = csv.reader(csv_file, delimiter=',', quotechar='|')
                row_index = 1
                csv_data_list = []
                for row in csv_data:
                    csv_data_list.append(row)

                for section_widget in self.section_widget_list:
                    for sub_widget in section_widget.sub_section_widget_list:
                        for trans_widget in sub_widget.translation_widget_list:
                            trans_widget.change_custom_text(csv_data_list[row_index][5])# Text at 6eme place
                            row_index+=1


    def __save_csv(self):
        os.makedirs(self.CSV_FOLDER, exist_ok=True)
        csv_name = pathlib.Path(self.file_loaded).name
        csv_name = csv_name.split('.')[0] + '.csv'
        with open(os.path.join(self.CSV_FOLDER, csv_name), 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

            csv_writer.writerow(['Section name', 'Sub section id', 'Offset address', 'Offset value', 'Text address', 'Text'])
            for section_widget in self.section_widget_list:
                section = section_widget.section
                for sub_section in section.subsection_list:
                    for trans in sub_section.translation_list:
                        csv_writer.writerow([section.section_name, sub_section.sub_section_id, trans.offset_address, trans.offset_value, trans.text_address, trans.custom_text])

    def __load_file(self, file_to_load: str = ""):
        file_to_load = os.path.join("OriginalFiles", "kernel.bin")  # For developing faster
        print(f"File to load: {file_to_load}")
        if not file_to_load:
            file_to_load = self.file_dialog.getOpenFileName(parent=self, caption="Find file", filter="*",
                                                            directory=os.getcwd())[0]
        if file_to_load:
            self.file_loaded = file_to_load

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

    def __load_text_from_file(self):
        # First we read all offset section
        for section_data in self.game_data.kernel_data_json["sections"]:
            #if section_data["section_offset"] != 0x0004:
            #    continue
            #if section_data["type"] != "data":
            #    continue
            #if not section_data["section_offset_text_linked"]:
            #    continue
            # Reading section
            offset_to_offset_section = section_data["section_offset"]
            offset_to_offset_section_data = self.current_file_data[offset_to_offset_section: offset_to_offset_section + section_data["size"]]
            offset_to_offset_section_data_int = int.from_bytes(offset_to_offset_section_data, byteorder="little")

            next_section_data = self.__get_next_section_data(section_data)
            if next_section_data:
                next_offset_to_offset_section = next_section_data["section_offset"]
                next_offset_to_offset_section_data = self.current_file_data[
                                                     next_offset_to_offset_section: next_offset_to_offset_section + next_section_data["size"]]
                next_offset_to_offset_section_data_int = int.from_bytes(next_offset_to_offset_section_data, byteorder="little")
            else:
                next_offset_to_offset_section_data_int = len(self.current_file_data)

            section = Section(game_data=self.game_data, section_offset_value=offset_to_offset_section_data_int, section_offset_address=section_data["section_offset"], nb_subsection=section_data["number_sub_section"],
                              subsection_size=section_data["sub_section_size"],
                              section_data=self.current_file_data[offset_to_offset_section_data_int:next_offset_to_offset_section_data_int],
                              section_name=section_data["section_name"], sub_section_sub_offset=section_data["sub_section_sub_offset"])

            # Now reading the text, as the section doesn't have the data of others section
            # First get all of text_address
            for sub_section in section.subsection_list:
                for translation in sub_section.translation_list:
                    translation.offset_address = section.section_offset_value + section.subsection_size * sub_section.sub_section_id + translation.offset_in_sub_section
                    offset_section_linked_info = \
                        [x for x in self.game_data.kernel_data_json["sections"] if x["section_offset"] == section_data["section_offset_text_linked"]][0]
                    offset_section_linked_data = self.current_file_data[
                                                 offset_section_linked_info["section_offset"]: offset_section_linked_info["section_offset"] +
                                                                                               offset_section_linked_info["size"]]
                    offset_section_linked_data_int = int.from_bytes(offset_section_linked_data, byteorder="little")
                    translation.text_address = offset_section_linked_data_int + translation.offset_value

            # Now getting the str
            for sub_index, sub_section in enumerate(section.subsection_list):
                for trans_index in range(len(sub_section.translation_list)):
                    if trans_index == len(sub_section.translation_list) - 1:  # Last one of translation list
                        if sub_index != len(section.subsection_list) - 1:  # If not last sub, we take the first trans from next sub
                            text_end_address = section.subsection_list[sub_index + 1].translation_list[0].text_address
                        else:  # Take the offset for next section
                            link_offset_data = \
                                [x for x in self.game_data.kernel_data_json['sections'] if x["section_offset"] == section_data["section_offset_text_linked"]][0]
                            link_next_offset_data = self.__get_next_section_data(link_offset_data)
                            if link_next_offset_data:  # There is a next section
                                text_end_address = link_next_offset_data["section_offset"]
                            else:  # Means it's the last section so we take the end of file
                                text_end_address = len(self.current_file_data)
                    else:
                        text_end_address = sub_section.translation_list[trans_index + 1].text_address
                    text_byte_data = self.current_file_data[sub_section.translation_list[trans_index].text_address: text_end_address]
                    text_str = self.game_data.translate_hex_to_str(text_byte_data)
                    sub_section.translation_list[trans_index].file_text = text_str
                    sub_section.translation_list[trans_index].custom_text = text_str

            self.section_widget_list.append(SectionWidget(section))
            self.layout_translation_lines.addWidget(self.section_widget_list[-1])
            #self.section_widget_list[-1].show()

    def __get_next_section_data(self, section_data_ref):
        next_section_data = section_data_ref
        for section_data in self.game_data.kernel_data_json["sections"]:
            if next_section_data["section_offset"] > section_data["section_offset"] > section_data_ref["section_offset"] or (
                    section_data["section_offset"] > section_data_ref["section_offset"] and next_section_data["section_offset"] == section_data_ref[
                "section_offset"]):
                next_section_data = section_data
        if next_section_data == section_data_ref:
            return None
        else:
            return next_section_data
