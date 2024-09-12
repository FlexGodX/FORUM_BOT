from aiogram import Router
from aiogram.types import Message
from lexicon.lexicon import Lexicon_ru


router = Router()

@router.message()
async def end(message: Message):
    await message.answer(text = Lexicon_ru['no_answer'] )