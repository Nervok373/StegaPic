import os
import random

from aiogram import Bot, Dispatcher, executor, types

import decrypt
import encrypt

# BOT_TOKEN = os.getenv("TOKEN")

# Initialize bot and dispatcher
bot = Bot(token="6258687980:AAHzJ8_9AVqQkgnWCtL2xldoQpHmpwvFdHM")
dp = Dispatcher(bot)

USERS = {}


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(f"Привет {user_name}, используя меня ты можешь "
                         f"спрятать текст в картинке, поддерживается английский"
                         f" и русский язык\nиспользуй /help "
                         f"чтобы получить подсказки.")


@dp.message_handler(commands=['help', '?', 'h', 'helpme'])
async def send_help(message: types.Message):
    await message.answer('''
Режимы:
    /into_pic - запись сообщение В изображение.
    /from_pic - чтение сообщение ИЗ изображение.

Методы(выбираются после режимов):
    /1 Использование user_id в качестве ключа.
        Вы загружаете только картинку и пишете текст, 
        а ключом является ваш id аккаунта.
        Вам не надо нечего дополнительного хранить,
        быстро и удобно. Но в определённых случаях
        может быть не безопасно.

    /2 Использование файла с ключом.
        Все изменения записываются в отдельный файл, 
        который нужен для расшифровки в будущем.

    /3 Получение(запись) текста из(в) .txt + использование 
        своего ключа. Текст вводиться не вручную 
        а читается с прислонного txt файла, 
        и в последующем записывается тоже в txt.
        В этом режиме можно вводить свою ключ-фразу, 
        и возможный текст не ограничивается 
        допустимой длиной сообщения.

! Внимание: при большом объёме текста бот может долго обрабатывать запрос !
    ''')


@dp.message_handler(commands=['into_pic', 'from_pic'])
async def into_picture(message: types.Message):
    com = "intoPic" if message.get_command() == "/into_pic" else "fromPic"
    USERS[message.from_user.id] = {'status': f'{com}_0'}

    await message.answer(
        'Выбери способ (подробнее о каждом способе: /help):\n'
        '/1 использование user_id в качестве ключа.\n'
        '/2 использование файла с ключом.\n'
        '/3 получение(запись) текста из(в) .txt + использование '
        '   своего ключа.')


# method handler
@dp.message_handler(commands=['1', '2', '3'])
async def method_one(message: types.Message):
    if USERS[message.from_user.id]['status'] == 'intoPic_0':
        USERS[message.from_user.id] = {'status': 'intoPic_1',
                                       'mood': message.get_command()[1:]}

        await message.answer('пришли фото (в виде файла, без сжатия)')

    elif USERS[message.from_user.id]['status'] == 'fromPic_0':
        USERS[message.from_user.id] = {'status': 'fromPic_1',
                                       'mood': message.get_command()[1:]}

        await message.answer('пришли фото (в виде файла, без сжатия)')
    else:
        await  message.answer('делай всё по порядку /help')


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def download_photo(message: types.Message):
    if USERS[message.from_user.id]['status'] == 'intoPic_1':

        USERS[message.from_user.id].update({'status': 'intoPic_2'})
        USERS[message.from_user.id].update(
            {'img path': f'tmp/img/{message.from_user.id}.'
                         f'{message.document.file_name.split(".")[1]}'})

        await message.document.download(
            destination_file=USERS[message.from_user.id]['img path'])

        if USERS[message.from_user.id]['mood'] == '3':
            await message.answer('теперь пришли файл с текстом(расширение txt)')
        else:
            await message.answer('теперь напишите что вы хотите скрыть в изображении')

    # take .txt file
    elif USERS[message.from_user.id]['status'] == 'intoPic_2':
        USERS[message.from_user.id].update({'status': 'intoPic_3'})
        if message.document.file_name.split(".")[1] != 'txt':
            os.remove(USERS[message.from_user.id]['img path'])
            USERS[message.from_user.id] = {"status": 'None', "mood": "None"}
            await message.answer("Это не txt файл, попробуй всё с начала.")

        else:
            USERS[message.from_user.id].update(
                {'txt path': f'tmp/txt/{message.from_user.id}.txt'})

            await message.document.download(
                destination_file=USERS[message.from_user.id]['txt path']
            )

            await message.answer('теперь напиши ключ-фразу,'
                                 ' пробелы и регистр имеют значение')

    elif USERS[message.from_user.id]['status'] == 'fromPic_1':
        USERS[message.from_user.id].update({'status': 'fromPic_2'})
        USERS[message.from_user.id].update(
            {'img path': f'tmp/img/{message.from_user.id}.png'})

        await message.document.download(
            destination_file=f'tmp/img/{message.from_user.id}.png')

        if USERS[message.from_user.id]['mood'] == '2':
            await message.answer('теперь пришли файл с ключом')
        elif USERS[message.from_user.id]['mood'] == '3':
            await message.answer('теперь напиши ключ фразу, '
                                 'пробелы и регистр имеют значение')
        else:
            await message.answer("/start_decrypt")

    elif USERS[message.from_user.id]['status'] == 'fromPic_2' and \
            USERS[message.from_user.id]['mood'] == '2':

        USERS[message.from_user.id].update({'status': 'fromPic_3'})
        USERS[message.from_user.id].update(
            {'keys path': f'tmp/keys/{message.from_user.id}.txt'})

        await message.document.download(
            destination_file=f'tmp/keys/{message.from_user.id}.txt')

        await message.answer("/start_decrypt")

    else:
        await message.answer("делай всё по порядку /help")


@dp.message_handler(commands=['start_encrypt'])
async def start_encrypting(message: types.Message):
    if (USERS[message.from_user.id]['status'] == 'intoPic_2' and
        USERS[message.from_user.id]['mood'] in ['1', '2']) or \
            USERS[message.from_user.id]['status'] == 'intoPic_3':

        if USERS[message.from_user.id]['mood'] == '3':
            with open(file=USERS[message.from_user.id]['txt path'], mode='r') as txt:
                _text = txt.read()
                txt.close()
        else:
            _text = USERS[message.from_user.id]['text']

        _key_word = ""
        if USERS[message.from_user.id]['mood'] == '1':
            _key_word = str(message.from_user.id)
        elif USERS[message.from_user.id]['mood'] == '3':
            _key_word = USERS[message.from_user.id]['text']

        _mood = '2' if USERS[message.from_user.id]['mood'] == '2' else '1'

        result = encrypt.stego_encrypt(
            path_img=USERS[message.from_user.id]['img path'],
            text=_text,
            keys_file_path=f'tmp/keys/{message.from_user.id}',
            encrypt_img_path=f'tmp/crypt_img/{message.from_user.id}',
            mood=_mood,
            key_word=_key_word)

        if not result:
            await message.answer(str(result))

        else:
            media_group = types.MediaGroup()

            new_random_name = ''.join([str(random.randint(0, 9)) for _ in range(10)])

            os.rename(f'tmp/crypt_img/{message.from_user.id}.png',
                      f'tmp/crypt_img/{new_random_name}.png')

            media_group.attach_document(
                open(f'tmp/crypt_img/{new_random_name}.png', 'rb'))

            if USERS[message.from_user.id]['mood'] == "2":
                media_group.attach_document(
                    open(f'tmp/keys/{message.from_user.id}.txt', 'rb'))

            await message.answer_media_group(media_group)

            if USERS[message.from_user.id]['mood'] == '2':
                os.remove(f'tmp/keys/{message.from_user.id}.txt')
            elif USERS[message.from_user.id]['mood'] == '3':
                os.remove(f'tmp/txt/{message.from_user.id}.txt')
            os.remove(f'tmp/crypt_img/{new_random_name}.png')
            os.remove(USERS[message.from_user.id]['img path'])

            USERS[message.from_user.id] = {'status': 'None',
                                           'mood': 'None',
                                           'text': ''}

            await message.answer('рад стараться')

    else:
        await message.answer('Я тебя не понял, скорее всего Вы делаете что то не по порядку.')


@dp.message_handler(commands=['start_decrypt'])
async def start_decrypting(message: types.Message):
    _key_word = ""
    if USERS[message.from_user.id]['mood'] == '1':
        _key_word = str(message.from_user.id)
    elif USERS[message.from_user.id]['mood'] == '3':
        _key_word = USERS[message.from_user.id]['text']

    str(message.from_user.id) if USERS[message.from_user.id][
                                     'mood'] == "1" else ""

    _mood = '2' if USERS[message.from_user.id]['mood'] == '2' else '1'

    text_in_pic = decrypt.stego_decrypt(
        path_img=USERS[message.from_user.id]['img path'],
        keys_file_path=USERS[message.from_user.id]['keys path'] if
        USERS[message.from_user.id]['mood'] == "2" else "",
        mood=_mood,
        key_word=_key_word
    )

    if text_in_pic["ok"]:
        if USERS[message.from_user.id]['mood'] == '3':
            with open(file=f'tmp/txt/{message.from_user.id}_out.txt',
                      mode='w') as txt:
                txt.write(text_in_pic['text'])
                txt.close()

                media_group = types.MediaGroup()

                media_group.attach_document(
                    open(f'tmp/txt/{message.from_user.id}_out.txt', 'rb'))

                await message.answer_media_group(media_group)

        else:
            await message.answer(text_in_pic["text"])
    else:
        await message.answer('кажется что-то пошло не так:\n' +
                             text_in_pic['text'])

    if USERS[message.from_user.id]['mood'] == '2':
        os.remove(f'tmp/keys/{message.from_user.id}.txt')
    elif USERS[message.from_user.id]['mood'] == '3':
        os.remove(f'tmp/txt/{message.from_user.id}_out.txt')

    USERS[message.from_user.id] = {'status': 'None', 'mood': 'None',
                                   'text': ''}
    os.remove(f'tmp/img/{message.from_user.id}.png')


@dp.message_handler()
async def echo(message: types.Message):
    if message.from_user.id not in USERS:
        USERS[message.from_user.id] = {"status": 'None'}

    if (USERS[message.from_user.id]['status'] == 'intoPic_2' and
        USERS[message.from_user.id]['mood'] in ['1', '2']) or \
            USERS[message.from_user.id]['status'] == 'intoPic_3':

        USERS[message.from_user.id].update({'text': message.text})

        await message.answer("/start_encrypt")

    elif USERS[message.from_user.id]['status'] == 'fromPic_2' and \
            USERS[message.from_user.id]['mood'] == '3':
        USERS[message.from_user.id].update({'text': message.text})

        await message.answer("/start_decrypt")
    else:
        await message.answer("Я тебя не понял, используй /help")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
