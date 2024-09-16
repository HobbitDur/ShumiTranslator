from PyQt6.QtCore import QSignalBlocker
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QTextEdit

from gamedata import GameData
from translation import Translation


class TranslationWidget(QWidget):

    def __init__(self, translation: Translation):
        QWidget.__init__(self)
        self.translation = translation
        self.__file_text_description_widget = QLabel("<b>Data read: </b>")
        self.__file_text_widget = QLabel()
        self.__file_text_widget.setText(self.translation.file_text)
        # self.__file_text_widget.setWordWrap(True)

        self.__custom_text_description_widget = QLabel("<b>Data modified: </b>")
        self.__custom_text_widget = QPlainTextEdit()
        self.__custom_text_widget.setPlainText(self.translation.custom_text)
        self.__custom_text_widget.textChanged.connect(self.__custom_text_changed)
        # self.__custom_text_widget.setMaximumHeight(28)

        self.__text_original_layout = QHBoxLayout()
        self.__text_original_layout.addSpacing(20)
        self.__text_original_layout.addWidget(self.__file_text_description_widget)
        self.__text_original_layout.addWidget(self.__file_text_widget)
        self.__text_original_layout.addStretch(1)

        self.__text_custom_layout = QHBoxLayout()
        self.__text_custom_layout.addSpacing(20)
        self.__text_custom_layout.addWidget(self.__custom_text_description_widget)
        self.__text_custom_layout.addWidget(self.__custom_text_widget)
        self.__text_custom_layout.addStretch(1)

        self.__main_layout = QVBoxLayout()
        self.__main_layout.addLayout(self.__text_original_layout)
        self.__main_layout.addLayout(self.__text_custom_layout)
        self.__main_layout.addStretch(1)

        self.setLayout(self.__main_layout)

    def __custom_text_changed(self):
        self.translation.custom_text = self.__custom_text_widget.toPlainText()

    def change_custom_text(self, custom_text):
        self.__custom_text_widget.setPlainText(custom_text)
