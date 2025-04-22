import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from python_aternos import Client
from AdminData import *
import time

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализация клиента Aternos
at_client = Client()
try:
    at_client.login(ADMIN_USERNAME, ADMIN_PASSWORD)
    logger.info("Успешное подключение к Aternos")
except Exception as e:
    logger.error(f"Ошибка подключения: {e}")
    raise

aternos = at_client.account
servers = aternos.list_servers()
serv = servers[0]


@dp.message(Command("start", "help"))
async def cmd_start(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        return await message.answer("🛑 Нет доступа")
        
    await message.answer(
        "<b>Aternos Control Bot</b>\n\n"
        "Доступные команды:\n"
        "/serverlist - список серверов\n"
        "/startserv - Запустить сервер\n"
        "/stopserv - Остановить сервер\n"
        "/restartserv - Перезагрузить сервер\n\n"
        "⚠️ Запуск сервера может занять несколько минут",
        parse_mode="HTML"
    )


async def check_server_status(status, interval=15, timeout=300):
    """Проверяет статус сервера с интервалом"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        serv.fetch()
        if serv.status == status:
            return True
        await asyncio.sleep(interval)
    return False


@dp.message(Command("startserv"))
async def cmd_startserv(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        return await message.answer("🛑 Нет доступа")
    
    status_msg = await message.answer("Запуск сервера...")
    try:
        serv.start()
        if await check_server_status(status="online"):
            await status_msg.edit_text("🟢 Сервер успешно запущен!")
        else:
            await status_msg.edit_text("⚠️ Сервер не запустился в течение 7.5 минут")
    except Exception as e:
        await message.answer(f"Error: {e}")


@dp.message(Command("stopserv"))
async def cmd_stopserv(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        return await message.answer("🛑 Нет доступа")
    
    status_msg = await message.answer("Остановка сервера...")
    try:
        serv.stop()
        if await check_server_status(status="offline"):
            await status_msg.edit_text("🟢 Сервер успешно остановлен!")
        else:
            await status_msg.edit_text("⚠️ Сервер не был остановлен")
    except Exception as e:
        await message.answer(f"Error: {e}")


@dp.message(Command("restartserv"))
async def cmd_restartserv(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        return await message.answer("🛑 Нет доступа")

    status_msg = await message.answer("Перезагрузка сервера...")
    try:
        serv.restart()
        if await check_server_status(status="online"):
            await status_msg.edit_text("🟢 Сервер успешно перезагружен!")
    except Exception as e:
        await message.answer(f"Error: {e}")


@dp.message(Command("serverlist"))
async def cmd_serverlist(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        return await message.answer("🛑 Нет доступа")

    if not servers:
        await message.answer("🛑 Сервера не найдены")
    else:
        await message.answer(f"Найдено серверов: {len(servers)}\n")
    
    for i, server in enumerate(servers, 1):
        # Обновляем данные сервера
        server.fetch()
        
        # Формируем информацию
        info = (
            f"🔹 Сервер #{i}\n"
            f"Имя: {server.subdomain or 'Без имени'}\n"
            f"Статус: {server.status}\n"
            f"Адрес: {server.address if hasattr(server, 'address') else 'N/A'}\n"
            f"Игроков: {getattr(server, 'players_count', 'N/A')}/{getattr(server, 'slots', 'N/A')}\n"
            f"Версия: {getattr(server, 'software', 'N/A')}\n"
        )
        await message.answer(info)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())