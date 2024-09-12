from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery

#Словарь для данных пользователей
user_dict: dict[int, dict[str, str | int | bool]] = {}

class FSMmessage(StatesGroup):
    create_topik_name = State()
    add_tag = State()
    write_tag = State()
    choice_send_message = State()
