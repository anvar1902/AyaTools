import asyncio
import shlex
import time

from html import escape
from pyrogram import Client, enums
from pyrogram.types import Message
from pyrogram.errors import Unauthorized, SessionPasswordNeeded, FloodWait, ChatIdInvalid, ChatSendGifsForbidden, \
    ChatForbidden, ChatInvalid, PeerIdInvalid, ActiveUserRequired, AuthKeyInvalid, AuthKeyPermEmpty, SessionExpired, \
    SessionRevoked, UserDeactivatedBan, AuthKeyUnregistered, UserDeactivated

from commands.base_model import Base_Command

class Command(Base_Command):
    command = "spam"
    description = ""
    syntax = "<сообщение> <кулдаун> [сообщения за повтор] [кулдаун повторов] [повторы]"
    def __init__(self, *args):
        super().__init__(*args)

    async def main(self, command_text, command_name, command_args, prefix, message):
        if not len(command_args) < 2:
            params = await self.validate_params(*command_args)
            data = {
                "chat_id": message.chat.id,
                "text": params[0],
                "interval": params[1],
                "count":  params[2],
                "delay":  params[3],
                "repeat_count": params[4]
            }
            if self.command in self.spec.tasks:
                for i in self.spec.tasks[self.command]:
                    if i.data["chat_id"] == data["chat_id"] and i.data["text"] == data["text"]:
                        raise ValueError(f"Задача {data["text"]} уже запущена в данном чате")
            await self.start(data)
        else:
            raise ValueError("Недостаточно аргументов")

    async def validate_params(self, text, interval, count = 1, delay = 0.5, repeat = -1, *args, **kwargs):
        try:
            text = str(text)
        except:
            raise ValueError("Сообщение должно быть строкой.")
        try:
            interval = int(interval)
            if interval <= 0: raise
        except:
            raise ValueError("Интервал должен быть положительным целым числом.")
        try:
            count = int(count)
            if count <= 0: raise
        except:
            raise ValueError("Количество сообщений должно быть положительным целым числом.")
        try:
            delay = float(delay)
            if delay < 0: raise
        except:
            raise ValueError("Задержка должна быть неотрицательным числом.")
        try:
            repeat = int(repeat)
            if repeat < -1: raise
        except:
            raise ValueError("Количество повторов должно быть целым числом, не меньше -1.")
        return text, interval, count, delay, repeat

    async def start(self, data):
        self.data = data
        if self.command in self.spec.tasks:
            self.spec.tasks[self.command].append(self)
        else:
            self.spec.tasks[self.command] = [self]
        if "last_use_time" in data:
            await asyncio.sleep(data["last_use_time"] - data["currect_time"])

        self.running = True
        executed_repeats = 0
        errors = 0
        while errors <= 10 and (data["repeat_count"] == -1 or executed_repeats < data["repeat_count"]):
            for _ in range(data["count"]):
                if not self.running or not self.spec.running:
                    self.spec.tasks[self.command].remove(self)
                    return
                try:
                    await self.client.send_message(data["chat_id"], data["text"])
                    errors = 0
                except (ChatForbidden, ChatInvalid, ChatIdInvalid, PeerIdInvalid) as e:
                    self.spec.logger.error(f"Невалидный chat_id: {data["chat_id"]}. Ошибка: {e}")
                    errors += 1
                    return
                except ConnectionError:
                    while self.running and self.spec.running:
                        try:
                            await asyncio.sleep(0.2)
                            await self.client.send_message(data["chat_id"], data["text"])
                            break
                        except ConnectionError: pass
                except Exception as e:
                    self.spec.logger.error(f"Ошибка при отправке сообщения: {e}", exc_info=e)
                    errors += 1
                await asyncio.sleep(data["delay"])
            executed_repeats += 1
            self.data["last_use_time"] = time.time()
            for wait in range(data["interval"]):
                if not self.running or not self.spec.running:
                    self.spec.tasks[self.command].remove(self)
                    return
                self.data["currect_time"] = time.time()
                await asyncio.sleep(0.96)
        self.spec.tasks[self.command].remove(self)

    async def stop(self):
        self.running = False
        self.spec.logger.info(f"Остановка команды {self.command}")


