# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 22:00:43 2024

@author: faustellar gpt4o
"""

import os
import requests
from zipfile import ZipFile
from media_processor import batch_convert_mp4_to_gif_or_png  # Import the new module
from concurrent.futures import ThreadPoolExecutor  # Import ThreadPoolExecutor

class TGBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, chat_id, text):
        url = f"{self.base_url}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        response = requests.post(url, data=data)
        return response.json()

    def send_sticker(self, chat_id, sticker_id):
        url = f"{self.base_url}/sendSticker"
        data = {"chat_id": chat_id, "sticker": sticker_id}
        response = requests.post(url, data=data)
        return response.json()

    def get_all_updates(self):
        url = f"{self.base_url}/getUpdates"
        response = requests.get(url)
        return response.json()

    def get_updates(self, params: dict):
        url = f"{self.base_url}/getUpdates"
        response = requests.get(url, params=params)
        return response.json()

    def get_last_update(self):
        updates = self.get_all_updates()
        if "result" in updates and len(updates["result"]) > 0:
            return updates["result"][-1]
        return None

    def get_chat_id(self, message):
        return message["message"]["chat"]["id"]

    def get_sticker_id(self, message):
        if "sticker" in message["message"]:
            return message["message"]["sticker"]["file_id"]
        return None

    def get_message_text(self, message):
        if "text" in message["message"]:
            return message["message"]["text"]
        return None

    def get_sticker_set(self, name):
        url = f"{self.base_url}/getStickerSet"
        params = {"name": name}
        response = requests.get(url, params=params)
        return response.json()
    
    def download_sticker(self, file_path, file_id, folder_path, is_animated):
        file_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        response = requests.get(file_url)
        if response.status_code == 200:
            file_extension = 'mp4' if is_animated else 'webp'
            with open(f'{folder_path}/{file_id}.{file_extension}', 'wb') as f:
                f.write(response.content)
            print(f'Downloaded {file_id}.{file_extension} in {folder_path}')
        else:
            print(f'Failed to download {file_id}')
    
    def download_sticker_pack(self, sticker_set_name, directory):
        sticker_set = self.get_sticker_set(sticker_set_name)
        if (sticker_set["ok"]):
            stickers = sticker_set["result"]["stickers"]
            if not os.path.exists(directory):
                os.makedirs(directory)
            for sticker in stickers:
                file_id = sticker["file_id"]
                file_info = self.get_file_info(file_id)
                file_path = file_info["result"]["file_path"]
                is_animated = sticker["is_animated"] or sticker["is_video"]
                self.download_sticker(file_path, file_id, directory, is_animated)
        else:
            print(f'Failed to get sticker set: {sticker_set_name}')

    def get_file_info(self, file_id):
        url = f"{self.base_url}/getFile"
        params = {"file_id": file_id}
        response = requests.get(url, params=params)
        return response.json()

    def download_sticker_pack_n(self, sticker_set_name, directory, num_threads=8):
        sticker_set = self.get_sticker_set(sticker_set_name)
        if sticker_set["ok"]:
            stickers = sticker_set["result"]["stickers"]
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            def download_sticker_wrapper(sticker):
                file_id = sticker["file_id"]
                file_info = self.get_file_info(file_id)
                file_path = file_info["result"]["file_path"]
                is_animated = sticker["is_animated"] or sticker["is_video"]
                self.download_sticker(file_path, file_id, directory, is_animated)
            
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                executor.map(download_sticker_wrapper, stickers)
        else:
            print(f'Failed to get sticker set: {sticker_set_name}')
