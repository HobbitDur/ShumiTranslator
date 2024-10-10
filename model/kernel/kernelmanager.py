import csv

from FF8GameData.gamedata import GameData, SectionType
from FF8GameData.GenericSection.listff8text import ListFF8Text
from model.kernel.kernelsectiondata import SectionData
from model.kernel.kernelsectionheader import SectionHeader


class KernelManager():
    def __init__(self, game_data: GameData):
        self.game_data = game_data
        self.section_list = []

    def save_file(self, file):
        current_offset = 0
        current_file_data = bytearray()

        # Then creating the file
        for index_section, section in enumerate(self.section_list):
            # First updating all offset on section data
            if section.type == SectionType.DATA and section.section_text_linked:
                section_text_linked = section.section_text_linked
                section_text_list = section_text_linked.get_text_list()
                section.set_all_offset(section_text_list)
            # Then updating text
            if section.type == SectionType.FF8_TEXT:
                section.update_data_hex()
                self.section_list[0].set_section_offset_value_from_id(index_section, current_offset)
            current_offset += len(section)

        for section in self.section_list:
            current_file_data.extend(section.get_data_hex())
        with open(file, "wb") as in_file:
            in_file.write(current_file_data)

    def load_file(self, file):
        current_file_data = bytearray()
        with open(file, "rb") as in_file:
            while el := in_file.read(1):
                current_file_data.extend(el)
        # First we read all offset section
        self.section_list = []
        # +1 for the number of section
        section_header = SectionHeader(game_data=self.game_data, data_hex=current_file_data[0:(len(
            self.game_data.kernel_data_json["sections"]) + 1) * SectionHeader.OFFSET_SIZE], name="header")
        self.section_list.append(section_header)
        for index, section_info in enumerate(self.game_data.kernel_data_json["sections"]):
            section_id = index + 1
            section_offset_value = self.section_list[0].get_section_offset_value_from_id(section_id)
            next_section_offset_value = self.section_list[0].get_section_offset_value_from_id(section_id + 1)
            own_offset = section_offset_value
            if next_section_offset_value is None:
                next_section_offset_value = len(current_file_data)
            if section_info["type"] == SectionType.DATA:
                new_section = SectionData(game_data=self.game_data, id=section_id, own_offset=own_offset,
                                          data_hex=current_file_data[own_offset:next_section_offset_value],
                                          subsection_nb_text_offset=section_info['sub_section_nb_text_offset'],
                                          name=section_info['section_name'])
                new_section.init_subsection(nb_subsection=section_info['number_sub_section'],
                                            subsection_sized=section_info['sub_section_size'])
            elif section_info["type"] == SectionType.FF8_TEXT:
                section_data_linked = [self.section_list[i] for i in range(1, len(self.section_list)) if
                                       section_info['section_offset_data_linked'] == self.section_list[
                                           0].get_section_header_offset_from_id(i)][0]
                new_section = ListFF8Text(game_data=self.game_data, id=section_id, own_offset=own_offset,
                                          data_hex=current_file_data[own_offset:next_section_offset_value],
                                          section_data_linked=section_data_linked,
                                          name=section_info['section_name'])
            else:
                new_section = None
                # new_section.init_subsection(nb_subsection=section_info['number_sub_section'], subsection_sized=section_info['sub_section_size'])
            self.section_list.append(new_section)

        for i, section in enumerate(self.section_list):
            if section.type == SectionType.FF8_TEXT:
                # Adding the link from data to text as text were not constructed yet.
                section.section_data_linked.section_text_linked = section
                # Initializing the text now that we can get all the offset
                section.init_text(section.section_data_linked.get_all_offset())

    def save_csv(self, csv_path):
        if csv_path:
            with open(csv_path, 'w', newline='', encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

                csv_writer.writerow(
                    ['Section data name', 'Section data id', 'Sub section data id', 'Data id', 'Section text id',
                     'Text id', 'Text'])
                for index_section, section in enumerate(self.section_list):
                    if section.type == SectionType.DATA and section.section_text_linked:
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

    def load_csv(self, csv_to_load, section_widget_list):
        if csv_to_load:
            with open(csv_to_load, newline='', encoding="utf-8") as csv_file:

                csv_data = csv.reader(csv_file, delimiter=';', quotechar='|')
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
                    # Managing this case as many people do the mistake.
                    text_loaded = text_loaded.replace('`', "'")
                    if text_loaded != "":  # If empty it will not be applied, so better be fast
                        for widget_index, widget in enumerate(section_widget_list):
                            if widget.section.type == SectionType.FF8_TEXT and widget.section.id == section_text_id:
                                section_widget_list[widget_index].set_text_from_id(text_id, text_loaded)