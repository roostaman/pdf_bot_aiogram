import os
import asyncio
import logging
import sys
import zipfile
import glob
import uuid
from decouple import config
from PyPDF2 import PdfReader, PdfWriter
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

# Your Telegram bot token
TOKEN = config('TOKEN')

# All handlers should be attached to the Router (or Dispatcher)
bot = Bot(token=TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))
dp = Dispatcher()

zip_files = glob.glob('/data/*.zip')


async def unzip(zip_files):
    if not os.path.exists('/data/extracted'):
        os.makedirs('/data/extracted')

    if zip_files:
        for zip_file in zip_files:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall('/data/extracted')
                zip_ref.close()

    return glob.glob('/data/extracted/*.pdf')


# add page from reader, but crop it to 1/4 size:
def crop_page(page_to_crop):
    page = page_to_crop
    page.mediabox.lower_right = (
        page.mediabox.right / 2,
        page.mediabox.top / 2,
    )
    return page


# crop and merge pdfs:
async def crop_and_merge(input_files):
    writer = PdfWriter()

    for file in input_files:
        with open(file, 'rb') as pdf_file:
            reader = PdfReader(pdf_file)

            for i in range(len(reader.pages)):
                page = reader.pages[i]
                cropped_page = crop_page(page_to_crop=page)
                writer.add_page(page=cropped_page)

    # write to output pdf file:
    myuuid = uuid.uuid4()
    output_path = f'/data/results/{myuuid}.pdf'

    with open(output_path, 'wb') as of:
        writer.write(of)
        of.close()

    with open(f'/data/results_back/{myuuid}.pdf', 'wb') as of:
        writer.write(of)
        of.close()
    return [output_path]


async def clear_directory(input_files, zip_files):
    # List < String > list = inout_files.name

    for file in input_files:
        # if (list.contains(file.name))
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")

    for file in glob.glob('/data/results/*'):
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")

    for file in zip_files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")


# command handler to start the bot:
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Salamaleikum, {html.bold(message.from_user.full_name)}! \nSkin mne .zip arhibnyi fail nakladnyh, i ya otpravlyu gotovyi fail dlya pechati na termoprintere.")


# Message handler to handle files
@dp.message(F.document)
async def handle_zip(message: Message):
    try:
        # Download the file:
        document = message.document
        if document.mime_type == 'application/zip':
            # Download the file:
            file_id = message.document.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            zip_uuid = uuid.uuid4()
            file_name = f"/data/{zip_uuid}.zip"

            # Download the zip file:
            await bot.download_file(file_path, file_name)

            # Unzip:
            zip_files = glob.glob('/data/*.zip')
            input_files = await unzip(zip_files)

            # Process PDFs:
            output_file = await crop_and_merge(input_files)

            # Send the merged PDF:
            try:
                new_file = FSInputFile(output_file[0])
                await message.reply_document(document=new_file)
            except Exception as e:
                print(f'Error occured: {e}')
                await message.reply('Ошибка при обработке документа:( ')

            await clear_directory(input_files, zip_files)

        else:
            await message.reply(f'Normalno obrashaisya so mnoi. Zhdu "arhivnyi" dokument)\nI tolko po odnomu. Tolpoi ne lez.')

    except Exception as e:
        print(f'An error occured: {e}')


@dp.message(F.text)
async def handle_text(message: Message):
    await message.reply('Otprav "nakladnoi" skachannyi iz kabineta prodavca.')


# main
async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
