from PyQt6.QtCore import QSignalBlocker
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QMessageBox

from kernel.kerneltext import KernelText


class TranslationWidget(QWidget):

    def __init__(self, translation: KernelText):
        QWidget.__init__(self)
        self.translation = translation
        self.__file_text_description_widget = QLabel("<b>Data read: </b>")
        self.__file_text_widget = QLabel()
        self.__file_text_widget.setText(self.translation.get_str())
        # self.__file_text_widget.setWordWrap(True)

        self.__custom_text_description_widget = QLabel("<b>Data modified: </b>")
        self.__custom_text_widget = QPlainTextEdit()
        self.__custom_text_widget.setPlainText(self.translation.get_str())
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
        try:
            self.translation.set_str(self.__custom_text_widget.toPlainText())
        except ValueError:

            message_box = QMessageBox()
            message_box.setText("For the moment, the tool don't allow to just write a forbidden char liike { or }.\n"
                                "If you want to write a var like {HP}, copy paste both bracket\n"
                                "If you want to delete them, delete them both at same time\n"
                                "Sorry for the inconvenience.")
            message_box.setIcon(QMessageBox.Icon.Critical)
            message_box.setWindowTitle("ShumiTranslator - Forbidden char")
            message_box.exec()
            with QSignalBlocker(self.__custom_text_widget):
                self.__custom_text_widget.setPlainText(self.translation.get_str())

        print(self.translation.get_str())


    def change_custom_text(self, custom_text):
        self.__custom_text_widget.setPlainText(custom_text)
