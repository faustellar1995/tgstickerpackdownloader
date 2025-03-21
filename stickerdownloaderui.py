# -*- coding: utf-8 -*-
"""
GUI program for downloading and converting Telegram stickers using PyQt.
"""

import sys
import os

# Add the uis directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'uis'))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
from TGBot import TGBot
from media_processor import batch_convert_mp4_to_gif_or_png
from pwd_manager import DirManager, DirManagerUI  # Update the path for pwd_manager

class StickerDownloaderUI(QWidget):
    def __init__(self):
        super().__init__()
        self.bot = TGBot("your-tokens")  # Use default token
        self.dir_manager = DirManager()  # Initialize DirManager
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Telegram Sticker Downloader')
        self.setGeometry(100, 100, 700, 100)  # Adjust height to fit new UI elements
        
        layout = QVBoxLayout()
        layout.setSpacing(5)  # Reduce spacing between elements

        h_layout = QHBoxLayout()  # Create a horizontal layout for the label, input, and buttons

        self.sticker_set_label = QLabel('Sticker Set Name:', self)
        h_layout.addWidget(self.sticker_set_label)
        
        self.sticker_set_input = QLineEdit(self)
        h_layout.addWidget(self.sticker_set_input)
        
        self.download_button = QPushButton('Download', self)  # Change text to 'Download'
        self.download_button.clicked.connect(self.download_sticker_pack)
        h_layout.addWidget(self.download_button)
        
        self.convert_button = QPushButton('Convert', self)  # Change text to 'Convert'
        self.convert_button.clicked.connect(self.convert_stickers)
        h_layout.addWidget(self.convert_button)

        layout.addLayout(h_layout)  # Add the horizontal layout to the main layout
        
        self.dir_manager_ui = DirManagerUI(self.dir_manager)  # Add DirManagerUI
        layout.addWidget(self.dir_manager_ui)
        
        self.setLayout(layout)

    def get_sticker_name(self):
        sticker_set_name = self.sticker_set_input.text()
        
        if not sticker_set_name:
            QMessageBox.warning(self, 'Input Error', 'Please provide Sticker Set Name.')
            return None
        
        # Process the input to take the last group if it contains "/"
        if "/" in sticker_set_name:
            sticker_set_name = sticker_set_name.split("/")[-1]
        
        return sticker_set_name

    def download_sticker_pack(self):
        sticker_set_name = self.get_sticker_name()
        
        if not sticker_set_name:
            return
        
        # Process the input to take the last group if it contains "/"
        if "/" in sticker_set_name:
            sticker_set_name = sticker_set_name.split("/")[-1]
        
        download_dir = self.dir_manager.get_dirs()[0] if self.dir_manager.get_dirs() else "stickers"
        directory = os.path.join(download_dir, sticker_set_name)
        
        self.bot.download_sticker_pack(sticker_set_name, directory)
        QMessageBox.information(self, 'Download Complete', f'Sticker pack "{sticker_set_name}" downloaded successfully.')

    def convert_stickers(self):
        if not self.bot:
            QMessageBox.warning(self, 'Bot Error', 'Please download a sticker pack first.')
            return
        
        sticker_set_name = self.get_sticker_name()
        download_dir = self.dir_manager.get_dirs()[0] if self.dir_manager.get_dirs() else "stickers"
        directory = os.path.join(download_dir, sticker_set_name)
        batch_convert_mp4_to_gif_or_png(directory)
        QMessageBox.information(self, 'Conversion Complete', 'MP4 files have been converted to GIF/PNG and zipped.')

    # Remove open_directory method
    # def open_directory(self):
    #     sticker_set_name = self.sticker_set_input.text()
    #     download_dir = self.dir_manager.get_dirs()[0] if self.dir_manager.get_dirs() else "stickers"
    #     directory = os.path.join(download_dir, sticker_set_name)
    #     
    #     if not os.path.exists(directory):
    #         QMessageBox.warning(self, 'Directory Error', 'The specified directory does not exist.')
    #         return
    #     
    #     # Use QFileDialog to open the directory
    #     QFileDialog.getExistingDirectory(self, 'Open Directory', directory)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StickerDownloaderUI()
    ex.show()
    sys.exit(app.exec_())
