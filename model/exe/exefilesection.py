from FF8GameData.FF8HexReader.section import Section
from FF8GameData.gamedata import GameData


class ExeFileSection(Section):
    def __init__(self, game_data: GameData, data_hex):
        Section.__init__(self, game_data=game_data, data_hex=data_hex, id=0, own_offset=0, name=".Exe")
        self._section_list = []
        if not self._game_data.exe_data_json:
            self._game_data.load_exe_data()
        self._lang = "english"
        self.__analyse_data()
    def __str__(self):
        return str("To be define")

    def __repr__(self):
        return self.__str__()


    def save_csv(self, csv_path):
      pass


    def load_csv(self, csv_to_load, section_widget_list):
       pass

    def __analyse_data(self):
        self.__analyse_lang()
        print(self._lang)
        
        name_offset = self._game_data.card_data_json["card_data_offset"]["eng_name"] + self.__get_lang_offset()
        self._section_list.append(Section(self._game_data, self._data_hex[0:name_offset], id=0, own_offset=0, name="Ignored start data"))
        print(self._data_hex[name_offset:100].hex())
        
        #self._section_list.append(Section(self._game_data, self._data_hex[name_offset:len(self)]))

    def __analyse_lang(self):
        if self._data_hex[self._game_data.exe_data_json["lang"]["offset"]] == self._game_data.exe_data_json["lang"][
            "english_value"]:
            self._lang = "English"
        elif self._data_hex[self._game_data.exe_data_json["lang"]["offset"]] == self._game_data.exe_data_json["lang"][
            "french_value"]:
            self._lang = "French"
        elif self._data_hex[self._game_data.exe_data_json["lang"]["offset"]] == self._game_data.exe_data_json["lang"][
            "german_value"]:
            self._lang = "German (not supported yet)"
        elif self._data_hex[self._game_data.exe_data_json["lang"]["offset"]] == self._game_data.exe_data_json["lang"][
            "spanish_value"]:
            self._lang = "Spanish (not supported yet)"
        elif self._data_hex[self._game_data.exe_data_json["lang"]["offset"]] == self._game_data.exe_data_json["lang"][
            "italian_value"]:
            self._lang = "Italian (not supported yet)"
        else:
            print(f"Unexpected language, value: {self._data_hex[self._game_data.exe_data_json["lang"]["offset"]]}")
            self._lang = "english"

    def __get_lang_offset(self):
        if self._data_hex[self._game_data.exe_data_json["lang"]["offset"]] == self._game_data.exe_data_json["lang"]["english_value"]:
            return 0
        elif self._data_hex[self._game_data.exe_data_json["lang"]["offset"]] == self._game_data.exe_data_json["lang"]["french_value"]:
            return self._game_data.card_data_json["card_data_offset"]["fr_offset"]
        else:
            print("Language not supported yet")
            return 0