import os

from aiogram import Bot, Dispatcher, executor, types

import decrypt
import encrypt

bot_token = os.getenv("TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

USERS = {

}


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(f"Привет {user_name}, используя меня ты можешь "
                         f"спрятать текст в картинке.\nиспользуй /help "
                         f"чтобы получить подсказки")


@dp.message_handler(commands=['help', '?', 'h', 'helpme'])
async def send_help(message: types.Message):
    await message.answer('/into_pic - запись сообщение в изображение\n'
                         '/from_pic - чтение сообщение из изображение')


@dp.message_handler(commands=['into_pic'])
async def text_into_picture(message: types.Message):
    USERS[message.from_user.id] = {'status': 'intoPic_0'}
    await message.answer('пришли фото (в виде файла, без сжатия)')


@dp.message_handler(commands=['from_pic'])
async def text_into_picture(message: types.Message):
    USERS[message.from_user.id] = {'status': 'fromPic_0'}
    await message.answer('пришли фото в котором зашифровано сообщение'
                         ' (в виде файла, без сжатия)')

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def download_photo(message: types.Message):
    if USERS[message.from_user.id]['status'] == 'intoPic_0':
        USERS[message.from_user.id] = {'status': 'intoPic_1'}
        USERS[message.from_user.id].update(
            {'img path': f'tmp/img/{message.from_user.id}'})

        await message.document.download(
            destination_file=f'tmp/img/{message.from_user.id}')

        await message.answer('теперь напишите что вы хотите скрыть в изображении')

    elif USERS[message.from_user.id]['status'] == 'fromPic_0':
        USERS[message.from_user.id] = {'status': 'fromPic_1'}
        USERS[message.from_user.id].update(
            {'img path': f'tmp/img/{message.from_user.id}.png'})

        await message.document.download(
            destination_file=f'tmp/img/{message.from_user.id}.png')

        await message.answer('теперь пришли файл с ключом')

    elif USERS[message.from_user.id]['status'] == 'fromPic_1':
        USERS[message.from_user.id].update({'status': 'fromPic_1'})
        USERS[message.from_user.id].update(
            {'keys path': f'tmp/keys/{message.from_user.id}.txt'})

        await message.document.download(
            destination_file=f'tmp/keys/{message.from_user.id}.txt')

        text_in_pic = decrypt.stega_decrypt(
            path_img=USERS[message.from_user.id]['img path'],
            keys_file_path=USERS[message.from_user.id]['keys path'])

        await message.answer(text_in_pic)

        USERS[message.from_user.id] = {'status': 'fromPic_1'}
        os.remove(f'tmp/keys/{message.from_user.id}.txt')
        os.remove(f'tmp/img/{message.from_user.id}.png')

    else:
        await message.answer("делай всё по порядку /help")


@dp.message_handler()
async def echo(message: types.Message):
    if message.from_user.id not in USERS:
        USERS[message.from_user.id] = {"status": 'None'}

    if  USERS[message.from_user.id]['status'] == 'intoPic_1':
        USERS[message.from_user.id].update({'text': str(message.text)})

        encrypt.stega_encrypt(
            path_img=USERS[message.from_user.id]['img path'],
            text=USERS[message.from_user.id]['text'],
            keys_file_path=f'tmp/keys/{message.from_user.id}',
            encrypt_img_path=f'tmp/crypt_img/{message.from_user.id}')

        media_group = types.MediaGroup()

        media_group.attach_document(open(f'tmp/keys/{message.from_user.id}.txt', 'rb'))
        media_group.attach_document(open(f'tmp/crypt_img/{message.from_user.id}.png', 'rb'))

        await message.answer_media_group(media_group)

        os.remove(f'tmp/keys/{message.from_user.id}.txt')
        os.remove(f'tmp/crypt_img/{message.from_user.id}.png')
        os.remove(USERS[message.from_user.id]['img path'])

        USERS[message.from_user.id] = {"status": 'None'}

    await message.answer("рад стараться")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
