from aiogram import Router,Bot,F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from lexicon.lexicon import Lexicon_ru
from config_data.config import Config, load_config
from FSM.fsm import *

from aiogram.filters import StateFilter,or_f
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

from Data_base.persistent_dict import PersistentDict

logger = logging.getLogger(__name__)

router= Router()
#Topics_new = Topics

config : Config = load_config()
bot = Bot(token = config.tg_bot.token)

chat_id = config.tg_group_id.id

Dict = PersistentDict('/home/FlexGod/Pivo_bot/FORUM_BOT/Data_base/dicts.json')
#Заменить на r"C:\Projects\PIVO_TEST\Data_base\dicts.json" во время тестов


@router.message(Command(commands='clear'))
async def create_topik_procesing_name(message: Message, state : FSMContext):
      await state.set_state(default_state)
      await state.clear()
      await message.answer(text = "Успешная очистка")

@router.message(Command(commands='cancel'))
async def create_topik_procesing_name(message: Message, state : FSMContext):
      await state.set_state(default_state)
      await message.answer(text = "Успешная отмена")


@router.message(CommandStart(),StateFilter(default_state))
async def process_start_command(message:Message):
    await message.answer(text = Lexicon_ru['/start'])

@router.message(Command(commands='info'),StateFilter(default_state))
async def proces_info(message:Message):
    await message.answer(text = Lexicon_ru['/info'])

@router.message(Command(commands='get_topics'), StateFilter(default_state))
async def get_topics(message: Message):
    textt = Lexicon_ru['/get_topics']
    for topic in Dict["Topics"]:
        textt += f"• {topic}\n"
    await message.answer(text=textt)

    
@router.message(Command(commands='create_topik'), F.from_user.username.in_(Dict["Admin_ids"]))
async def create_topik_procesing(message: Message, state : FSMContext):
        await message.answer(text = 'Введите название темы не больше 60 символов(Можете добавить emoji)\n\nЕсли хотите отменить создание темы нажмите /cancel')
        await state.set_state(FSMmessage.create_topik_name)

@router.message(Command(commands='create_topik'))
async def create_topik_procesing(message: Message, state : FSMContext):
        await message.answer(text = 'У вас нет прав')


@router.callback_query(F.data == "ADD_TOPIC", F.from_user.username.in_(Dict["Admin_ids"]))
async def create_topik_procesing_callback(callback: CallbackQuery, state : FSMContext):
        await callback.answer(text = 'Введите название темы не больше 60 символов(Можете добавить emoji)\n\nЕсли хотите отменить создание темы нажмите /cancel')
        if callback.message.reply_to_message:
         await callback.message.edit_text(
            text= "Введите название темы не больше 60 символов(Можете добавить emoji)\n\nЕсли хотите отменить создание темы нажмите /cancel",
            reply_markup=None
        )
        await state.set_state(FSMmessage.create_topik_name)

@router.callback_query(F.data == "ADD_TOPIC")
async def create_topik_procesing_callback(callback: CallbackQuery, state : FSMContext):
        await callback.answer(text = 'У вас нет прав')
 

@router.message(StateFilter(FSMmessage.create_topik_name), lambda x: len(x.text) <= 60, F.text != '/clear',F.text != '/cancel')
async def create_topik_procesing_name(message: Message, state : FSMContext):
        forum_topik = await bot.create_forum_topic(chat_id= chat_id,name= message.text)
        logger.debug(Dict["Topics"])
        Dict.update_subdict('Topics',{message.text : str(forum_topik.message_thread_id)})
        await message.answer(text= "Тема создана\n\nОтправьте сообщение еще раз и тема появиться в списке")
        await state.set_state(default_state)
    
@router.message(StateFilter(FSMmessage.create_topik_name))
async def create_topik_procesing_name(message: Message, state : FSMContext):
        await message.answer(text= "Неподходящий текст, попробуйте еще раз\n\nЕсли хотите отменить создание темы нажмите /cancel")


     