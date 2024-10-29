import os

from FF8GameData.ExeSection.exefile import SectionExeFile
import csv

from FF8GameData.gamedata import GameData, MsdType


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

    def save_file(self, folder):
        file_scan = os.path.join(folder, "battle_scans.msd")
        card_name = os.path.join(folder, "card_names.msd")
        with open(file_scan, "wb") as f:
            f.write(self.exe_section.produce_msd(MsdType.SCAN_TEXT))
        with open(card_name, "wb") as f:
            f.write(self.exe_section.produce_msd(MsdType.CARD_NAME))

    def load_file(self, file_exe):
        exe_hex = bytearray()
        with open(file_exe, "rb") as file:
            exe_hex.extend(file.read())

        self.exe_section = SectionExeFile(self.game_data, exe_hex)

    def save_csv(self, csv_path):
        if csv_path:
            with open(csv_path, 'w', newline='', encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=GameData.find_delimiter_from_csv_file(csv_path), quotechar='|', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(
                    ['Section data name', 'Section id', 'Text Sub id', 'Text'])
                card_name_section = self.exe_section.get_section_card_name()
                for card_index, card_ff8_text in enumerate(card_name_section.get_text_section().get_text_list()):
                    csv_writer.writerow([card_name_section.name, card_name_section.id, card_index, card_ff8_text.get_str()])
                scan_section = self.exe_section.get_section_scan_text()
                for scan_index, scan_ff8_text in enumerate(scan_section.get_text_section().get_text_list()):
                    csv_writer.writerow([scan_section.name, scan_section.id, scan_index, scan_ff8_text.get_str()])

    def load_csv(self, csv_to_load, section_widget_list):
        if csv_to_load:
            with open(csv_to_load, newline='', encoding="utf-8") as csv_file:
                csv_data = csv.reader(csv_file, delimiter=GameData.find_delimiter_from_csv_file(csv_to_load), quotechar='|')
                #  ['Section data name', 'Section id', 'Text Sub id', 'Text']
                for row_index, row in enumerate(csv_data):
                    if row_index == 0:  # Ignoring title row
                        continue
                    # section_data_name = row[0]
                    section_id = int(row[1])
                    text_sub_id = int(row[2])
                    text_loaded = row[3]

                    if text_loaded == "":
                        continue
                    # Managing this case as many people do the mistake.
                    text_loaded = text_loaded.replace('`', "'")
                    for widget_index, widget in enumerate(section_widget_list):
                        if widget.section.id == section_id:
                            section_widget_list[widget_index].set_text_from_id(text_sub_id, text_loaded)
                            break
