from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from lexicon.lexicon import Lexicon_ru

from Data_base.persistent_dict import PersistentDict

import logging
logger = logging.getLogger(__name__)
#------ Клавиатура согласия на тег -------
yes_tag_button = InlineKeyboardButton(
    text= "Да",
    callback_data= "Yes_Add_tag"
)

no_tag_button = InlineKeyboardButton(
    text= "Нет",
    callback_data= "No_Add_tag"
)

choice_tag_kb = InlineKeyboardMarkup(inline_keyboard=[[yes_tag_button],[no_tag_button]])


#--------Клавиатура выбора темы------------
def keyboard_choice_topic_register():
    Dict = PersistentDict(r"C:\Projects\PIVO_BOT_v1\Data_base\dicts.json")
    inline_topics_kb_builder = InlineKeyboardBuilder()

    otmenbutton = InlineKeyboardButton(
    text = "ОТМЕНА",
    callback_data= "CANCEL"
    )

    inline_topics_kb_builder.add(otmenbutton)

    def generate_inline_keyboard(topicss: dict[str, str]) -> InlineKeyboardMarkup:
        # Создаем список для хранения строк кнопок
        buttons = []
        # Проходим по каждому элементу словаря
        for title, callback_data in topicss.items():
            # Создаем инлайн-кнопку
            button = InlineKeyboardButton(text=title, callback_data=f"forward_to_{callback_data}")
            # Добавляем кнопку в строку
            buttons.append(button)

        # Создаем и возвращаем объект InlineKeyboardMarkup
        return  buttons
    # Генерируем инлайн-клавиатуру
    addTopicButton = InlineKeyboardButton(
    text = "ДОБАВИТЬ ТЕМУ\n\n(Только для администраторов)",
    callback_data= "ADD_TOPIC"
    )
    inline_topics_kb_builder.row(*generate_inline_keyboard(Dict["Topics"]),width=3)
    inline_topics_kb_builder.row(addTopicButton,width=1)

    logger.debug("||||||||||||||||||||||||||||||| Клавиатура инициализированна")
    return inline_topics_kb_builder

#-----------------------------------------


#----------------------------------------------
