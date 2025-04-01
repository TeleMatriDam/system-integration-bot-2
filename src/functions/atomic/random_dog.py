"""Модуль для реализации функции бота для получения случайных картинок собак."""

import logging
from typing import List
import requests
import telebot
from telebot import types
from telebot.callback_data import CallbackData
from bot_func_abc import AtomicBotFunctionABC


class AtomicRandomDogBotFunction(AtomicBotFunctionABC):
    """Реализация функции бота для получения случайных картинок собак."""

    commands: List[str] = ["randomdog", "rdog", "randog"]
    authors: List[str] = ["TeleMatriDam"]
    about: str = "Генератор случайных картинок собак!"
    description: str = """Вызывает случайное изображение собаки из API.
    Можно выбрать количество картинок (1-3).
    Пример вызова функции - /dog
    """
    state: bool = True

    bot: telebot.TeleBot
    dog_keyboard_factory: CallbackData

    def set_handlers(self, bot: telebot.TeleBot):
        """Set message handlers"""

        self.bot = bot
        self.dog_keyboard_factory = CallbackData('dog_button', prefix=self.commands[0])

        @bot.message_handler(commands=self.commands)
        def random_dog_message_handler(message: types.Message):
            markup = self.__gen_markup()
            bot.send_message(chat_id=message.chat.id, text="Choose qty pic:", reply_markup=markup)

        @bot.callback_query_handler(func=None, config=self.dog_keyboard_factory.filter())
        def dog_keyboard_callback(call: types.CallbackQuery):
            callback_data: dict = self.dog_keyboard_factory.parse(callback_data=call.data)
            if callback_data['dog_button'] == "back":
                self.random_dog_message_handler(call.message)
            else:
                count = int(callback_data['dog_button'])
                images = self.__get_random_dog_images(count)
                for img in images:
                    bot.send_photo(chat_id=call.message.chat.id, photo=img)

    def __get_random_dog_images(self, count=1):
        """Fetches a given number of random dog images from Random Dog API."""
        images = []
        attempts = 0
        while len(images) < count and attempts < count * 2:  # Extra attempts to get valid images
            try:
                response = requests.get("https://random.dog/woof.json", timeout=5)
                if response.status_code == 200:
                    img_url = response.json().get("url")
                    if img_url and img_url.endswith(('jpg', 'jpeg', 'png', 'gif')):
                        images.append(img_url)
                attempts += 1
            except requests.exceptions.RequestException as ex:
                logging.exception(ex)
                attempts += 1
        return images

    def __gen_markup(self):
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 3
        btn = types.InlineKeyboardButton
        factory = self.dog_keyboard_factory
        markup.add(
            btn("1", callback_data=factory.new(dog_button="1")),
            btn("2", callback_data=factory.new(dog_button="2")),
            btn("3", callback_data=factory.new(dog_button="3"))
        )
        return markup
