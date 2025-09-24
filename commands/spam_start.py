import asyncio
import shlex
import time

from pyrogram import Client, enums
from pyrogram.types import Message
from pyrogram.errors import Unauthorized, SessionPasswordNeeded, FloodWait, ChatIdInvalid, ChatSendGifsForbidden, \
    ChatForbidden, ChatInvalid, PeerIdInvalid, ActiveUserRequired, AuthKeyInvalid, AuthKeyPermEmpty, SessionExpired, \
    SessionRevoked, UserDeactivatedBan, AuthKeyUnregistered, UserDeactivated

class Command:
    command = "spam"
    description = ""
    def __init__(self, client: Client, spec):
        self.client = client
        self.spec = spec

    async def main_handler(self, command_text, message: Message):
        command = shlex.split(command_text)
        self.command_name = command[0]
        command_args = command[1:]
        try:
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
        except ValueError as e:
            self.spec.logger.error(e)
            me = await self.client.get_me()
            if me.is_premium:
                error_message = (
                    f"<b><emoji id=\"5327938799345349736\">🩸</emoji>"
                    f"<emoji id=\"5328162635860948105\">🩸</emoji>"
                    f"<emoji id=\"5328162635860948105\">🩸</emoji>"
                    f"<emoji id=\"5307644490461231051\">🩸</emoji>"
                    f"<emoji id=\"5328162635860948105\">🩸</emoji>"
                    f"\n<emoji id=\"5341633328338451873\">❗</emoji>️ {e}"
                    f"\n"
                    f"\n<emoji id=\"5341633328338451873\">❗</emoji>️Команда должна выглядеть так:"
                    f"\n<emoji id=\"5463258057607760727\">🩸</emoji>{self.spec.prefixs[0]}{self.command_name} <сообщение> <кулдаун> [сообщения за повтор] [кулдаун повторов] [повторы]"
                    f"\n"
                    f"\n<emoji id=\"5341633328338451873\">❗</emoji>Вы написали:</b>"
                    f"\n<emoji id=\"5463258057607760727\">🩸</emoji><code>{self.spec.prefixs[0]}{command_text}</code>"
                )
            else:
                error_message = (
                    f"E R R O R"
                    f"\n❗️{e}"
                    f"\n"
                    f"\n❗️Команда должна выглядеть так:"
                    f"\n❤️{self.spec.prefixs[0]}{self.command_name} <сообщение> <кулдаун> [сообщения за повтор] [кулдаун повторов] [повторы]"
                    f"\n"
                    f"\n❗️Вы написали:"
                    f"\n❤️<code>{self.spec.prefixs[0]}{command_text}</code>"
                )
            await self.client.send_message(message.chat.id, error_message, parse_mode=enums.ParseMode.HTML)

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


