from aiogram import F,Bot,types
from aiogram import Router
from aiogram.types import Message, CallbackQuery, input_media,InputMediaPhoto,InputMediaVideo,InputMediaDocument,InputMediaAudio
from aiogram.enums import ParseMode
from aiogram.filters import BaseFilter, or_f
from FSM.fsm import *
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
import re
#from aiogram.utils.media_group import MediaGroupBuilder
import logging #для логирования



from config_data.config import Config, load_config
from lexicon.lexicon import Lexicon_ru
from keyboards.keyboards import keyboard_choice_topic_register,choice_tag_kb


#-------------------------------------------------------------------
router = Router()
#-------------------------------------------------------------------
logger = logging.getLogger(__name__)

config: Config = load_config()
bot = Bot(token= config.tg_bot.token)
#-------------------------------------------------------------------
chat_id = config.tg_group_id.id
#-------------------------------------------------------------------
media_group_temp_storage = {}
media_group_temp_storage['caption'] = {}

#-------------------------------------------------------------------

#inline_topics_kb_builder = keyboard_choice_topic_register()



#Кастомные фильтры
#---------------------------------------------
class WordCountFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        # Считаем количество слов в сообщении
        if message.text is not None and len(message.text.split()) >= 30:
             return True
        else:
             return False
    

URL_REGEX = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
#----------------------------------------------


#Сделать хендлер,который на медиагруппу реагирует
@router.message(F.media_group_id)
async def media_group_process(message: Message,state: FSMContext):

    media_group_id = message.media_group_id
    
    if media_group_id not in media_group_temp_storage:
        media_group_temp_storage[media_group_id] = []

        
      

    if message.caption is not None:
         media_group_caption = message.caption

    
         if message.caption_entities is not None:
                 flag = 0
                 i = 1
                 for x in message.caption_entities:
                      if x.type == "text_link":
                           if flag == 0:
                                media_group_caption = media_group_caption + '\n\nСсылки из текста:'
                                flag = 1
                           media_group_caption = media_group_caption + f'\n{i}) {x.url}'
                           i += 1

         if message.forward_origin:
              if message.forward_origin.type == 'channel' and message.forward_origin.chat.username is not None:
                     media_group_caption = media_group_caption + f'\n\nКанал: @{message.forward_origin.chat.username}' f'\nПользователь: #{message.chat.username}'
                     media_group_temp_storage['caption'][media_group_id] = media_group_caption
              elif message.forward_origin.type == 'user' and message.forward_origin.sender_user.username is not None:
                     media_group_caption = media_group_caption + f'\n\nАвтор: @{message.forward_origin.sender_user.username}\nПользователь: #{message.chat.username}'
                     media_group_temp_storage['caption'][media_group_id] = media_group_caption
              elif message.forward_origin.type == 'hidden_user':
                     media_group_caption = media_group_caption + f'\n\nАвтор: Анонимус\nПользователь: #{message.chat.username}' 
                     media_group_temp_storage['caption'][media_group_id] = media_group_caption
              else:
                   media_group_caption = media_group_caption + f'\n\nПользователь: #{message.chat.username}'
                   media_group_temp_storage['caption'][media_group_id] = media_group_caption
         else:
            media_group_caption = media_group_caption + f'\n\nПользователь: #{message.chat.username}'
            media_group_temp_storage['caption'][media_group_id] = media_group_caption
        
        #media_group_temp_storage['caption'] = media_group_caption + f'\n\nКанал: @{message.forward_origin.chat.username}' f'\n #{message.chat.username}'
    
    # Инициализация временного хранилища для медиагруппы, если еще не создано

        

        # Добавление текущего файла в медиагруппу
    if message.photo:
        media_group_temp_storage[media_group_id].append(InputMediaPhoto(media=message.photo[-1].file_id))
    elif message.video:
        media_group_temp_storage[media_group_id].append(InputMediaVideo(media=message.video.file_id))
    elif message.document:
        media_group_temp_storage[media_group_id].append(InputMediaDocument(media=message.document.file_id))
    elif message.audio:
         media_group_temp_storage[media_group_id].append(InputMediaAudio(media=message.audio.file_id))
    
    
    await state.update_data(previous_message = message)
    if message.caption is not None:
        await message.reply(text= "Добавить тег/теги?",reply_markup= choice_tag_kb)
        await state.set_state(FSMmessage.add_tag)



@router.message(or_f(F.photo,F.video,F.document,F.audio,F.forward_date, WordCountFilter(),lambda message: re.search(URL_REGEX, message.text)))
async def forward_message(message: Message,state : FSMContext):
    logger.debug("Хендлер пересланного сообщения")
    inline_topics_kb_builder = keyboard_choice_topic_register()
    await state.update_data(previous_message = message)
    previous_message = message
    await message.reply(
        text= "Добавить тег/теги?",
        reply_markup= choice_tag_kb
    )
    await state.set_state(FSMmessage.add_tag)


@router.callback_query(StateFilter(FSMmessage.add_tag),F.data == "Yes_Add_tag")
async def choice_tag(callback : CallbackQuery, state : FSMContext):
     await callback.answer()
     await callback.message.edit_text(text= "Введите тег/теги(без решетки)\nчтобы написать несколько тегов напишите их через пробел\n\nЧтобы отменить дейсвие нажмите /cancel")
     await state.set_state(FSMmessage.write_tag)

#Если тег соответсвует условиям
@router.message(StateFilter(FSMmessage.write_tag), lambda x: len(x.text) <= 60, F.text != '/clear',F.text != '/cancel',lambda x: "#" not in x.text)
async def choice_tag(message :Message, state : FSMContext):
     await state.update_data(Tags = message.text.split( ))
     await state.set_state(FSMmessage.choice_send_message)

     inline_topics_kb_builder = keyboard_choice_topic_register()

     state_data = await state.get_data()
     previous_message = state_data.get('previous_message')
     await previous_message.reply(text="Выберите тему", reply_markup= inline_topics_kb_builder.as_markup())


#Если тег не соответсвует условиям
@router.message(StateFilter(FSMmessage.write_tag))
async def choice_tag_wrong(message :Message, state : FSMContext):
     await message.answer(text = "Неверный формат тега/тегов, попробуйте еще раз")

     
@router.callback_query(StateFilter(FSMmessage.add_tag),F.data == "No_Add_tag")
async def choice_tag(callback : CallbackQuery, state : FSMContext):
     inline_topics_kb_builder = keyboard_choice_topic_register()
     state_data = await state.get_data()
     previous_message = state_data.get('previous_message')
     await callback.answer()
     await callback.message.edit_text(text = "Выберите тему",reply_markup=inline_topics_kb_builder.as_markup())
     await state.set_state(FSMmessage.choice_send_message)


@router.callback_query(F.data.startswith('CANCEL'),~StateFilter(default_state))
async def cancale_choice(callback: CallbackQuery,state : FSMContext):
    if callback.message.reply_to_message:
         await callback.message.edit_text(
            text= "Выбор отменен",
            reply_markup=None
        )
    await state.set_state(default_state) 
    await callback.answer()   
         


@router.callback_query(F.data.startswith('forward_to_'),StateFilter(FSMmessage.choice_send_message))
async def forward_previous_message(callback: CallbackQuery,state : FSMContext):
    if callback.message.reply_to_message:

        previous_message : Message
        Tags : list [str] = []

        # Получаем предыдущее сообщение
        state_data = await state.get_data()
        previous_message = state_data.get('previous_message')

        # ID темы (топика) в чате, в который нужно переслать сообщение
        topic_id = int(callback.data[11:])

        await callback.message.edit_text(
            text= Lexicon_ru['the choice is made'],
            reply_markup=None
        )
        

        state_data = await state.get_data()
        test_tags = state_data.get("Tags")
        if  test_tags is not None:
             Tags = test_tags
        
        tags_str : str = ''
        if len(Tags) > 0:
             tags_str += '\nТеги: '
             for i in range(len(Tags)):
                tags_str += '#' + Tags[i]
                tags_str += ' '
        await state.update_data(Tags = [])

        # Если сообщение текстовое
        if previous_message.text is not None:
            text1 = previous_message.html_text
                        

            if previous_message.forward_origin:
                if previous_message.forward_origin.type == 'channel' and previous_message.forward_origin.chat.username is not None:
                     text1 =  text1 + f'\n\nКанал: @{previous_message.forward_origin.chat.username}' f'\nПользователь: #{previous_message.chat.username}' +  tags_str
                elif previous_message.forward_origin.type == 'user' and previous_message.forward_origin.sender_user.username is not None:
                     text1 =  text1 + f'\n\nАвтор: @{previous_message.forward_origin.sender_user.username}\nПользователь: #{previous_message.chat.username}' +  tags_str
                elif previous_message.forward_origin.type == 'hidden_user':
                     text1 =  text1 + f'\n\nАвтор: Аноним\nПользователь: #{previous_message.chat.username}' +  tags_str
                else:
                     text1 =  text1 + f'\n\nПользователь: #{previous_message.chat.username}' +  tags_str
            else:
                text1 =  text1 + f'\n\nПользователь: #{previous_message.chat.username}' +  tags_str

            await bot.send_message(
                chat_id=chat_id,
                message_thread_id=topic_id,
                parse_mode='HTML',
                text= text1
            )


        elif previous_message.media_group_id is not None:

            media_group_id = previous_message.media_group_id

            caption_media =  media_group_temp_storage['caption'][media_group_id]
            caption_media += tags_str

            if len(caption_media) > 1023:
                media_group_temp_storage[media_group_id][0].caption = 'Подпись в сообщении ниже'
                await bot.send_media_group(
                chat_id=chat_id,
                message_thread_id=topic_id,
                media=media_group_temp_storage[media_group_id],  # используем file_id
                )
                await bot.send_message(
                chat_id=chat_id,
                message_thread_id=topic_id,
                parse_mode='HTML',
                text = caption_media
                )
            else:
                media_group_temp_storage[media_group_id][0].caption = caption_media
                await bot.send_media_group(
                chat_id= chat_id,  # ID чата
                message_thread_id=topic_id,
                media=media_group_temp_storage[media_group_id]
            )


            # Отправляем медиагруппу в другой чат
            
            await callback.message.reply(text = Lexicon_ru['sucsess_forward'])
            # Удаляем временные данные после отправки
            del media_group_temp_storage[media_group_id]

        # Если сообщение содержит фото
        elif previous_message.photo is not None:

            caption1 = previous_message.html_text if previous_message.html_text is not None else ' '

            
            '''if previous_message.caption_entities is not None:
                 flag = 0
                 i = 1
                 for x in previous_message.caption_entities:
                      if x.type == "text_link":
                           if flag == 0:
                                caption1 = caption1 + '\n\nСсылки из текста:'
                                flag = 1
                           caption1 = caption1 + f'\n{i}) {x.url}'
                           i += 1'''
                      
            if previous_message.forward_origin:
                if previous_message.forward_origin.type == 'channel' and previous_message.forward_origin.chat.username is not None:
                     caption1 = caption1 + f'\n\nКанал: @{previous_message.forward_origin.chat.username}' f'\nПользователь: #{previous_message.chat.username}' +  tags_str
                elif previous_message.forward_origin.type == 'user' and previous_message.forward_origin.sender_user.username is not None:
                     caption1 = caption1 + f'\n\nАвтор: @{previous_message.forward_origin.sender_user.username}\nПользователь: #{previous_message.chat.username}' +  tags_str

                elif previous_message.forward_origin.type == 'hidden_user':
                     caption1 = caption1 + f'\n\nАвтор: Аноним\nПользователь: #{previous_message.chat.username}' +  tags_str
                else:
                     caption1 = caption1 + f'\n\nПользователь: #{previous_message.chat.username}' +  tags_str
            else:
                caption1 = caption1 + f'\n\nПользователь: #{previous_message.chat.username}' +  tags_str

            if len(caption1) > 1023:

                await bot.send_photo(
                chat_id=chat_id,
                message_thread_id=topic_id,
                photo=previous_message.photo[-1].file_id,  # используем file_id
                parse_mode='HTML',
                caption= 'Подпись в сообщении ниже'
                )
                await bot.send_message(
                chat_id=chat_id,
                message_thread_id=topic_id,
                parse_mode='HTML',
                text = caption1
                )
            else:
                 await bot.send_photo(
                chat_id=chat_id,
                message_thread_id=topic_id,
                photo=previous_message.photo[-1].file_id,  # используем file_id
                parse_mode='HTML',
                caption= caption1
            )
                 
            await callback.message.reply(text = Lexicon_ru['sucsess_forward'])

        # Если сообщение содержит видео
        elif previous_message.video is not None:

            caption1 = previous_message.html_text if previous_message.caption is not None else ' '

            '''if previous_message.caption_entities is not None:
                 flag = 0
                 i = 1
                 for x in previous_message.caption_entities:
                      if x.type == "text_link":
                           if flag == 0:
                                caption1 = caption1 + '\n\nСсылки из текста:'
                                flag = 1
                           caption1 = caption1 + f'\n{i}) {x.url}'
                           i += 1'''
                           
            if previous_message.forward_origin:
                if previous_message.forward_origin.type == 'channel' and previous_message.forward_origin.chat.username is not None:
                     caption1 = caption1 + f'\n\nКанал: @{previous_message.forward_origin.chat.username}' f'\nПользователь: #{previous_message.chat.username}' +  tags_str
                elif previous_message.forward_origin.type == 'user' and previous_message.forward_origin.sender_user.username is not None:
                     caption1 = caption1 + f'\n\nАвтор: @{previous_message.forward_origin.sender_user.username}\nПользователь: #{previous_message.chat.username}' +  tags_str
                elif previous_message.forward_origin.type == 'hidden_user':
                     caption1 = caption1 + f'\n\nАвтор: Аноним\nПользователь: #{previous_message.chat.username}' +  tags_str
                else:
                     caption1 = caption1 + f'\n\nПользователь: #{previous_message.chat.username}' +  tags_str
            else:
                caption1 = caption1 + f'\n\nПользователь: #{previous_message.chat.username}' +  tags_str


            if len(caption1) > 1023:

                await bot.send_video(
                chat_id=chat_id,
                message_thread_id=topic_id,
                video=previous_message.video.file_id,  # используем file_id
                parse_mode='HTML',
                caption= 'Подпись в сообщении ниже'
                )
                await bot.send_message(
                chat_id=chat_id,
                message_thread_id=topic_id,
                parse_mode='HTML',
                text = caption1
                )
            else:
                await bot.send_video(
                chat_id=chat_id,
                message_thread_id=topic_id,
                video=previous_message.video.file_id,  # используем file_id
                parse_mode='HTML',
                caption= caption1
            )
                 
            await callback.message.reply(text = Lexicon_ru['sucsess_forward'])

        # Если сообщение содержит документ
        elif previous_message.document is not None:

            caption1 = previous_message.html_text if previous_message.html_text is not None else ' '

            '''if previous_message.caption_entities is not None:
                 flag = 0
                 i = 1
                 for x in previous_message.caption_entities:
                      if x.type == "text_link":
                           if flag == 0:
                                caption1 = caption1 + '\n\nСсылки из текста:'
                                flag = 1
                           caption1 = caption1 + f'\n{i}) {x.url}'
                           i += 1'''

            if previous_message.forward_origin:
                
                if previous_message.forward_origin.type == 'channel' and previous_message.forward_origin.chat.username is not None:
                     caption1 = caption1 + f'\n\nКанал: @{previous_message.forward_origin.chat.username}' f'\nПользователь: #{previous_message.chat.username}' +  tags_str
                elif previous_message.forward_origin.type == 'user' and previous_message.forward_origin.sender_user.username is not None:
                     caption1 = caption1 + f'\n\nАвтор: @{previous_message.forward_origin.sender_user.username}\nПользователь: #{previous_message.chat.username}' +  tags_str
                elif previous_message.forward_origin.type == 'hidden_user':
                     caption1 = caption1 + f'\n\nАвтор: Аноним\nПользователь: #{previous_message.chat.username}' +  tags_str
                else:
                     caption1 = caption1 + f'\n\nПользователь: #{previous_message.chat.username}' +  tags_str
            else:
                
                caption1 = caption1 + f'\n\nПользователь: #{previous_message.chat.username}' +  tags_str
            
            if len(caption1) > 1023:

                await bot.send_document(
                chat_id=chat_id,
                message_thread_id=topic_id,
                document=previous_message.document.file_id,  # используем file_id
                parse_mode='HTML',
                caption= 'Подпись в сообщении ниже'
                )
                await bot.send_message(
                chat_id=chat_id,
                message_thread_id=topic_id,
                parse_mode='HTML',
                text = caption1
                )
            else:
                await bot.send_document(
                chat_id=chat_id,
                message_thread_id=topic_id,
                document=previous_message.document.file_id,  # используем file_id
                parse_mode='HTML',
                caption= caption1
            )
                 
            await callback.message.reply(text = Lexicon_ru['sucsess_forward'])

        # Если сообщение содержит аудио
        elif previous_message.audio is not None:

            caption1 = previous_message.html_text if previous_message.html_text is not None else ' '

            '''if previous_message.caption_entities is not None:
                 flag = 0
                 i = 1
                 for x in previous_message.caption_entities:
                      if x.type == "text_link":
                           if flag == 0:
                                caption1 = caption1 + '\n\nСсылки из текста:'
                                flag = 1
                           caption1 = caption1 + f'\n{i}) {x.url}'
                           i += 1'''

            if previous_message.forward_origin:
                if previous_message.forward_origin.type == 'channel' and previous_message.forward_origin.chat.username is not None:
                     caption1 = caption1 + f'\n\nКанал: @{previous_message.forward_origin.chat.username}' + f'\nПользователь:#{previous_message.chat.username}' +  tags_str
                elif previous_message.forward_origin.type == 'user' and previous_message.forward_origin.sender_user.username is not None:
                     caption1 = caption1 + f'\n\nАвтор: @{previous_message.forward_origin.sender_user.username}\nПользователь: #{previous_message.chat.username}' +  tags_str
                elif previous_message.forward_origin.type == 'hidden_user':
                     caption1 = caption1 + f'\n\nАвтор: Аноним\nПользователь: #{previous_message.chat.username}' +  tags_str
                else:
                     
                     caption1 = caption1 + f'\n\nПользователь: #{previous_message.chat.username}' +  tags_str
            else:
                
                caption1 = caption1 + f'\n\nПользователь: #{previous_message.chat.username}' +  tags_str

            
            if len(caption1) > 1023:

                await bot.send_audio(
                chat_id=chat_id,
                message_thread_id=topic_id,
                audio=previous_message.audio.file_id,  # используем file_id
                parse_mode='HTML',
                caption= 'Подпись в сообщении ниже'
                )
                await bot.send_message(
                chat_id=chat_id,
                message_thread_id=topic_id,
                parse_mode='HTML',
                text = caption1
                )
            else:
                await bot.send_audio(
                chat_id=chat_id,
                message_thread_id=topic_id,
                audio=previous_message.audio.file_id,  # используем file_id
                parse_mode='HTML',
                caption= caption1
            )
                
            await callback.message.reply(text = Lexicon_ru['sucsess_forward'])
        #Реакция на гифку,или аудио    
        '''elif previous_message.audio or previous_message.animation:
             logger.debug('Аудио или гифка')
             await bot.forward_message(
                chat_id=chat_id,
                from_chat_id= previous_message.chat.id,
                message_thread_id=topic_id,
             )'''     
    else:
        await callback.message.reply(text = Lexicon_ru['fail_forward'])

    await state.set_state(default_state)    
    await callback.answer()
    