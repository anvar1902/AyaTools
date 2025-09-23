import os
import platform

if platform.system() != "Windows":
    #import uvloop
    #uvloop.install()
    pass

from logging_setup import setup_logger
import commands

import asyncio
import orjson
import aiofiles
import logging
import time
import glob
import threading
from pyrogram import Client, filters, types
from pyrogram.errors import Unauthorized, SessionPasswordNeeded, FloodWait, ChatIdInvalid, ChatSendGifsForbidden, \
    ChatForbidden, ChatInvalid, PeerIdInvalid, ActiveUserRequired, AuthKeyInvalid, AuthKeyPermEmpty, SessionExpired, \
    SessionRevoked, UserDeactivatedBan, AuthKeyUnregistered, UserDeactivated
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler

API_ID = 25068392
API_HASH = 'aef0aea08e40cd1690290fb3df431766'
VERSION = "1.0.0 Release"
admin_id = "@Doctor_wh"

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | [%(levelname)s] | [%(threadName)s] | %(name)s | %(filename)s.%(funcName)s(%(lineno)d) | %(message)s"
)
system_logger = setup_logger('SystemLogger', "system_logger.log")
system_logger.propagate = False
system_logger.setLevel(logging.INFO)
system_logger.info("-" * 30)
system_logger.info("Available Commands:")
for i in commands.ALL_COMMANDS.keys():
    system_logger.info(i)
system_logger.info("-" * 30)

def out_user_info(session_file, user: types.User):
    system_logger.info("-" * 30)
    system_logger.info(f"Файл сессии: {session_file}.session")
    system_logger.info(f"ID: {user.id}")
    system_logger.info(f"Username: {user.username}")
    system_logger.info(f"Name: {user.full_name}")
    system_logger.info("-" * 30)

class AyaClient:
    def __init__(self, session_f: str, session_str: str, client_name):
        self.saving = False
        self.session = session_f
        self.session_string = session_str
        self.logger = setup_logger(client_name, f"{session_f}.log")
        self.commands = commands.ALL_COMMANDS
        self.prefixs = ["c."]
        self.tasks = {}

    def start(self):
        self.running = True
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.app = Client(
            self.session,
            api_hash=API_HASH, api_id=API_ID,
            app_version=VERSION,
            hide_password=False, session_string=self.session_string, in_memory=True
        )
        self.app.add_handler(MessageHandler(self.new_message_handler, filters.me))
        self.loop.run_until_complete(self.load_config())

        while self.running:
            try:
                self.loop.run_until_complete(self.main())
            except (SessionPasswordNeeded, Unauthorized):
                break
            except Exception as e:
                self.logger.error(exc_info=e)
                time.sleep(1)

    async def main(self):
        try:
            async with self.app:
                while self.running:
                    await asyncio.sleep(2)
                    if self.saving == False:
                        await self.save_config()
        except FloodWait as e:
            self.logger.warning(f"FloodWait {e.value} секунд")
            await asyncio.sleep(e.value)
        except (SessionPasswordNeeded, Unauthorized):
            raise
        except Exception as e:
            self.logger.error(f"Ошибка соединения", exc_info=e)
            try:
                await self.app.stop()
            except: pass
            if self.app.is_initialized: await self.app.terminate()
            if self.app.is_connected: await self.app.disconnect()

    async def new_message_handler(self, client: Client, message: Message):
        for prefix in self.prefixs:
            if message.text.startswith(prefix):
                command_text = message.text.removeprefix(prefix)
                for command_prefix, command_obj in self.commands.items():
                    if command_text.startswith(command_prefix):
                        await command_obj(client, self).main_handler(command_text, message)
                        self.logger.info(f"{command_prefix} Запущен")

    async def load_config(self):
        self.logger.info("Загрузка данных с файла конфига...")
        try:
            async with aiofiles.open(f"{self.session}_config.json", "r") as f:
                cfg_json = orjson.loads(await f.read())

            if "prefixs" in cfg_json:
                self.prefixs = list(cfg_json["prefixs"])
                self.logger.info("Префиксы успешно загружены")

            if "tasks" in cfg_json and type(cfg_json["tasks"]) is dict:
                restored_task = []
                for task_name, tasks_data in cfg_json["tasks"].items():
                    for task_data in tasks_data:
                        restored_task.append(asyncio.create_task(
                            self.commands[task_name](self.app, self).start(task_data)
                        ))
                self.logger.info("Задачи успешно восстановлены")

            if "commands" in cfg_json:
                for old, new in cfg_json["commands"].items():
                    self.commands[new] = self.commands.pop(old, None)
                self.logger.info("Изменения команд успешно загружены")
        except FileNotFoundError:
            self.logger.info("Не найден файл конфигов, будут настройки по умолчанию")
        except orjson.JSONDecodeError as e:
            self.logger.warning("Json файл конфига повреждён либо недействителен", exc_info=e)
            tr = 0
            while True:
                broken_file_name = f"{self.session}_config.broken{tr}.json"
                try:
                    os.rename(f"{self.session}_config.json", broken_file_name)
                    break
                except FileExistsError:
                    self.logger.warning(f"{broken_file_name} уже существует, пытаемся создать {broken_file_name}")
                    tr += 1
            self.logger.info(f"Создана копия недействительного конфига: {broken_file_name}")

    async def save_config(self):
        self.saving = True
        cfg_json = {
            "prefixs": self.prefixs,
            "tasks": {},
            "commands": {}
        }
        for command_name, command_data in self.tasks.items():
            cfg_json["tasks"][command_name] = []
            for task_data in command_data:
                cfg_json["tasks"][command_name].append(task_data.data)
        for old_name, new_name in zip(commands.ALL_COMMANDS, self.commands.keys()):
            if old_name != new_name:
                cfg_json["commands"][old_name] = new_name

        dst_path = f"{self.session}_config.json"
        tmp_path = dst_path + ".tmp"
        async with aiofiles.open(tmp_path, "wb") as f:
            await f.write(orjson.dumps(cfg_json))
            await f.flush()
        await asyncio.to_thread(os.replace, tmp_path, dst_path)
        self.saving = False

    def stop(self):
        self.running = False
        self.logger.warning("Завершение работы")



sessions_obj = []
sessions_threads = []
sessions_files = glob.glob('sessions/*.session')
if sessions_files:
    for i in range(len(sessions_files)):
        session_file = sessions_files[i].removesuffix('.session')
        session_test = Client(
            session_file,
            api_hash=API_HASH, api_id=API_ID,
            app_version=VERSION,
            hide_password=False, no_updates=True
        )
        try:
            with session_test:
                session_string = session_test.export_session_string()
                user = session_test.get_users("me")
                if user.is_frozen:
                    raise Unauthorized
                out_user_info(session_file, user)
                if user.username:
                    name = user.username
                else:
                    name = user.id
            sessions_obj.append(AyaClient(session_file, session_string, name))
            sessions_threads.append(
                    threading.Thread(
                    target=sessions_obj[i].start,
                    daemon=True,
                    name=name
                )
            )
            sessions_threads[i].start()
        except (ActiveUserRequired,AuthKeyInvalid, AuthKeyPermEmpty, AuthKeyUnregistered, Unauthorized,
                SessionExpired, SessionPasswordNeeded, SessionRevoked, UserDeactivated, UserDeactivatedBan) as e:
            system_logger.warning(f'{session_file} Не авторизован')
            try:
                session_test.stop()
            except: pass
            os.remove(sessions_files[i])
            if len(sessions_files) < 2:
                sessions_files = glob.glob('sessions/*.session')
if not sessions_files:
    system_logger.info("У вас нету сессий, завершаем скрипт...")
    time.sleep(5)
    os.abort()

while 1:
    try:
        time.sleep(5)

        system_logger.info("-" * 30)
        for t in threading.enumerate():
            system_logger.info(f"Поток: {t.name}, идентификатор: {t.ident}, живой: {t.is_alive()}")
        system_logger.info("-" * 30)
    except KeyboardInterrupt:
        system_logger.warning("Завершение программы!!!")
        for session in sessions_obj:
            session.stop()
        while set(sessions_threads) & set(threading.enumerate()):
            time.sleep(0.2)
        system_logger.info("Программа успешно завершена!")
        break
    except Exception as e:
        pass

