import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

START_TEXT = (
"Привет, мой дорогой друг 👋\n"
"Ты попал в продажу воскресшего 🔥\n"
"Выбери, что хочешь купить 👇"
)

# Кнопки с товарами
@router.message(Command("start"))
async def start(message: Message):
keyboard = InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="🛒 Товар 1", callback_data="item_1")],
[InlineKeyboardButton(text="🛒 Товар 2", callback_data="item_2")],
[InlineKeyboardButton(text="🛒 Товар 3", callback_data="item_3")],
])
await message.answer(START_TEXT, reply_markup=keyboard)

# Ответ на нажатие кнопки
@router.callback_query(F.data.startswith("item_"))
async def item_selected(callback, bot: Bot):
await callback.answer()
await callback.message.answer(f"Ты выбрал: {callback.data}")

# ==== Вебхук для Railway ====
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_SECRET = "my-secret"
WEBHOOK_URL = f"{os.getenv('RAILWAY_PUBLIC_DOMAIN', 'https://example.com')}{WEBHOOK_PATH}"

async def on_startup(app):
await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET)

async def on_shutdown(app):
await bot.session.close()

def main():
app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

SimpleRequestHandler(
dispatcher=dp,
bot=bot,
secret_token=WEBHOOK_SECRET,
).register(app, path=WEBHOOK_PATH)

setup_application(app, dp, bot=bot)
web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
main()
