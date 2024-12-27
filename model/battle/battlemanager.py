import pathlib
import csv

from FF8GameData.gamedata import GameData
from FF8GameData.GenericSection.listff8text import ListFF8Text
from IfritAI.IfritAI.ennemy import Ennemy


class BattleManager:
    def __init__(self, game_data: GameData):

        self.ennemy_list = []
        self.section_text_list = []
        self.file_list = []
        self.game_data = game_data

    def __str__(self):
        return str(self.ennemy_list)

    def __repr__(self):
        return self.__str__()

    def reset(self):
        self.ennemy_list = []
        self.section_text_list = []
        self.file_list = []

    def add_file(self, com_file):
        self.file_list.append(com_file)
        ennemy = Ennemy(self.game_data)
        ennemy.load_file_data(com_file, self.game_data)
        ennemy.analyse_loaded_data(self.game_data)
        self.ennemy_list.append(ennemy)
        self.section_text_list.append(
            ListFF8Text(game_data=self.game_data, data_hex=bytearray(), id=len(self.section_text_list), own_offset=0, name=ennemy.info_stat_data['monster_name']))

        for text in ennemy.battle_script_data['battle_text']:
            self.section_text_list[-1].add_text(self.game_data.translate_str_to_hex(text))

    def get_section_list(self):
        return self.section_text_list

    def save_all_file(self):
        for i in range(len(self.section_text_list)):
            if self.section_text_list[i]:
                self.section_text_list[i].update_data_hex()
                offset = 0
                for j, text in enumerate(self.section_text_list[i].get_text_list()):
                    self.ennemy_list[i].battle_script_data['text_offset'][j] = offset
                    self.ennemy_list[i].battle_script_data['battle_text'][j] = text
                    offset += len(text)
                self.ennemy_list[i].write_data_to_file(self.game_data, self.file_list[i])

    def save_csv(self, csv_path):
        if csv_path:
            with open(csv_path, 'w', newline='', encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=GameData.find_delimiter_from_csv_file(csv_path), quotechar='|', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(['Monster name', 'Section id', 'File name', 'Text Sub id', 'Text'])
                for index_section, section in enumerate(self.section_text_list):
                    for ff8text in section.get_text_list():
                        file_name = pathlib.Path(self.file_list[index_section]).name
                        csv_writer.writerow([section.name, section.id, file_name, ff8text.id, ff8text.get_str()])

    def load_csv(self, csv_to_load, section_widget_list):
        if csv_to_load:
            with open(csv_to_load, newline='', encoding="utf-8") as csv_file:
                csv_data = csv.reader(csv_file, delimiter=GameData.find_delimiter_from_csv_file(csv_to_load), quotechar='|')
                #  ['Monster name', 'Section id', 'File name', 'Text Sub id', 'Text']
                for row_index, row in enumerate(csv_data):
                    if row_index == 0:  # Ignoring title row
                        continue
                    # section_data_name = row[0]
                    section_id = int(row[1])
                    # file_name =row[2]
                    text_sub_id = int(row[3])
                    text_loaded = row[4]

                    if text_loaded == "":
                        continue
                    # Managing this case as many people do the mistake.
                    text_loaded = text_loaded.replace('`', "'")
                    for widget_index, widget in enumerate(section_widget_list):
                        if widget.section.id == section_id:
                            section_widget_list[widget_index].set_text_from_id(text_sub_id, text_loaded)
                            break
