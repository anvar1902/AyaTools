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
    command = "command"
    description = ""
    syntax = f"{escape("<edit>")} <Старое название> <Новое название>"
    def __init__(self, client: Client, spec):
        self.client = client
        self.spec = spec

    async def main_handler(self, command_text, message: Message):
        command = shlex.split(command_text)
        self.command_name = command[0]
        command_args = command[1:]
        prefix = self.spec.prefixs[0]
        try:
            if not len(command_args) < 3:
                operation = command_args[0]
                old_command = command_args[1]
                new_command = command_args[2]
                if operation == "edit":
                    if not new_command in self.spec.commands.keys():
                        if old_command in self.spec.commands.keys():
                            self.spec.commands[new_command] = self.spec.commands.pop(old_command, None)
                            await self.client.send_message(
                                message.chat.id,
                                f"Название {new_command} успешно установлена для команды {old_command}✅"
                            )
                        else:
                            raise ValueError(f"Такой команды не существует")
                    else:
                        raise ValueError("Данное название команды уже существует")
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
                    f"\n<emoji id=\"5463258057607760727\">🩸</emoji>{prefix}{self.command_name} {self.syntax}"
                    f"\n"
                    f"\n<emoji id=\"5341633328338451873\">❗</emoji>Вы написали:</b>"
                    f"\n<emoji id=\"5463258057607760727\">🩸</emoji><code>{prefix}{command_text}</code>"
                )
            else:
                error_message = (
                    f"E R R O R"
                    f"\n❗️{e}"
                    f"\n"
                    f"\n❗️Команда должна выглядеть так:"
                    f"\n❤️{prefix}{self.command_name} {self.syntax}"
                    f"\n"
                    f"\n❗️Вы написали:"
                    f"\n❤️<code>{prefix}{command_text}</code>"
                )
            await self.client.send_message(message.chat.id, error_message, parse_mode=enums.ParseMode.HTML)


