import asyncio
import shlex
import time

from html import escape
from pyrogram import Client, enums
from pyrogram.types import Message
from pyrogram.errors import Unauthorized, SessionPasswordNeeded, FloodWait, ChatIdInvalid, ChatSendGifsForbidden, \
    ChatForbidden, ChatInvalid, PeerIdInvalid, ActiveUserRequired, AuthKeyInvalid, AuthKeyPermEmpty, SessionExpired, \
    SessionRevoked, UserDeactivatedBan, AuthKeyUnregistered, UserDeactivated

class Command:
    command = "prefix"
    description = ""
    def __init__(self, client: Client, spec):
        self.client = client
        self.spec = spec

    async def main_handler(self, command_text, message: Message):
        command = shlex.split(command_text)
        self.command_name = command[0]
        command_args = command[1:]
        try:
            if not len(command_args) < 2 or (not len(command_args) < 1 and command_args[0] == "list"):
                params = await self.validate_params(*command_args)
                operation = params[0]
                new_prefix = params[1]
                if operation == "add":
                    if not new_prefix in self.spec.prefixs:
                        self.spec.prefixs.append(new_prefix)
                        await self.client.send_message(message.chat.id, f"Префикс {new_prefix} успешно добавлен✅")
                    else:
                        raise ValueError("Данный префикс уже существует")
                elif operation == "remove":
                    if new_prefix in self.spec.prefixs:
                        self.spec.prefixs.remove(new_prefix)
                        await self.client.send_message(message.chat.id, f"Префикс {new_prefix} успешно удалён✅")
                    else:
                        raise ValueError("Данного префикса не существует")
                elif operation == "list":
                    result = '\n'.join(pref for pref in self.spec.prefixs)
                    await self.client.send_message(message.chat.id, f"Список префиксов: \n{result}")
                else:
                    raise ValueError("Такой операции не существует")
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
                    f"\n<emoji id=\"5463258057607760727\">🩸</emoji>{self.spec.prefixs[0]}{self.command_name} {escape("<add/remove/list>")} <префикс>"
                    f"\n"
                    f"\n<emoji id=\"5341633328338451873\">❗</emoji>Вы написали:</b>"
                    f"\n<emoji id=\"5463258057607760727\">🩸</emoji><code>{self.spec.prefixs[0]}{command_text}</code>"
                )
            else:
                error_message = (
                    f"❌Неверный синтаксис команды!"
                    f"{e}"
                    f"🤩Синтаксис: {self.spec.prefixs[0]}{self.command_name} {escape("<add/remove/list>")} <префикс>"
                    f"⚜️Ваша команда: <code>{self.spec.prefixs[0]}{command_text}</code>"
                )
            await self.client.send_message(message.chat.id, error_message, parse_mode=enums.ParseMode.HTML)

    async def validate_params(self, operation, new_prefix = "", *args, **kwargs):
        try:
            text = str(operation)
            if not text in ["add", "remove", "list"]: raise
        except:
            raise ValueError("Неверная или несуществующая операция.")
        try:
            new_prefix = str(new_prefix)
        except:
            raise ValueError("Неверный префикс.")
        return text, new_prefix


