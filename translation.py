from gamedata import GameData


class Translation():
    def __init__(self, game_data: GameData, file_text="", custom_text="", text_address=0, offset_address=0, offset_in_sub_section=0, offset_value=0):
        self.game_data = game_data
        self.file_text = file_text
        self.custom_text = custom_text
        self.text_address = text_address
        self.offset_in_sub_section = offset_in_sub_section
        self.offset_address = offset_address
        self.offset_value = offset_value

    def __str__(self):
        text = f"Translation: | Offset_addr: {self.offset_address} - offset_value: {self.offset_value} - text_addr: {self.text_address} - file_text: {self.file_text}  |"
        return text

    def __repr__(self):
        return self.__str__()
