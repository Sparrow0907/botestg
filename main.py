from fastapi import FastAPI, Request
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from contextlib import asynccontextmanager  # Добавьте этот импорт


load_dotenv()


# --- НОВЫЙ способ установки вебхука (для FastAPI) ---
@asynccontextmanager
async def lifespan(app):
    # ВАЖНО: замените URL на ваш реальный адрес (например, от ngrok)
    # Адрес должен быть доступен из интернета
    webhook_url = os.getenv("WEBHOOK")
    
    try:
        await bot.set_webhook(url=webhook_url)
        print(f"Webhook установлен на {webhook_url}")
    except Exception as e:
        print (f"Произошла ошибка {e}" )

    yield  # Важно! Разделяет код запуска и остановки

    # Код, который выполняется ПРИ ОСТАНОВКЕ
    await bot.delete_webhook()
    print("🔄 Webhook удален")


app = FastAPI(lifespan=lifespan)  # Передаем lifespan при создании приложения

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):

    await message.answer("Привет!")

@dp.message(~Command("vlad", "rita", "start")) # Все сообщения которые не являются командами
async def echo(message:types.Message):

    await message.answer(message.text)


@dp.message(Command("vlad"))
async def vlad(message: types.Message):

    await message.answer("Влад,ты дура!")

@dp.message(Command("rita"))
async def rita(message: types.Message):

    await message.answer("Рита,ты красавица!")


@app.get("/ping")
async def ping():
    # Получаем информацию о текущем вебхуке
    webhook_info = await bot.get_webhook_info()
    expected_url = os.getenv("WEBHOOK")  # тот URL, который должен быть установлен

    # Если вебхук не установлен или URL не совпадает – переустанавливаем
    if webhook_info.url != expected_url:
        # Для надёжности можно сначала удалить старый вебхук (необязательно)
        # await bot.delete_webhook()
        await bot.set_webhook(url=expected_url)
        return {
            "status": "webhook updated",
            "old_url": webhook_info.url,
            "new_url": expected_url
        }

    # Всё в порядке
    return {"status": "ok", "webhook_url": webhook_info.url}

@app.get("/webhook")
async def webhook():
    return {"status": "ok", "message": "Webhook endpoint. Use POST for updates"}

# --- Эндпоинт для вебхука ---
# Telegram будет присылать обновления (сообщения) на этот адрес
@app.post("/webhook")
async def webhook(request: Request):


    # Получаем JSON-данные от Telegram
    json_data = await request.json()
    # Превращаем их в объект Update (тип из aiogram)
    update = types.Update(**json_data)
    # Передаём обновление диспетчеру, чтобы он нашёл нужный обработчик
    await dp.feed_update(bot, update)
    # Отвечаем Telegram, что всё приняли
    return{"ok": True }


    # # Этот код выполняется ПРИ ОСТАНОВКЕ (опционально)
    # await bot.delete_webhook()
    # print("🔄 Webhook удален")

