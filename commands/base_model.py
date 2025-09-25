import asyncio
import shlex
import time

from html import escape
from pyrogram import Client, enums
from pyrogram.types import Message
from pyrogram.errors import Unauthorized, SessionPasswordNeeded, FloodWait, ChatIdInvalid, ChatSendGifsForbidden, \
    ChatForbidden, ChatInvalid, PeerIdInvalid, ActiveUserRequired, AuthKeyInvalid, AuthKeyPermEmpty, SessionExpired, \
    SessionRevoked, UserDeactivatedBan, AuthKeyUnregistered, UserDeactivated



class Base_Command:
    command = "cmd"
    description = "Описание"
    syntax = f"<Обязательно> [Не обязательно]"
    def __init__(self, client: Client, spec):
        self.client = client
        self.spec = spec

    async def main_handler(self, command_text, message: Message):
        command = shlex.split(command_text)
        command_name = command[0]
        command_args = command[1:]
        prefix = self.spec.prefixs[0]
        try:
            await self.main(command_text, command_name, command_args, prefix, message)
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
                    f"\n<emoji id=\"5341633328338451873\">❗</emoji>️ {escape(e.args[0])}"
                    f"\n"
                    f"\n<emoji id=\"5341633328338451873\">❗</emoji>️Команда должна выглядеть так:"
                )
                if len(self.syntax.split("\n")) == 1:
                    error_message = error_message + (
                        f"\n<emoji id=\"5463258057607760727\">🩸</emoji>{escape(prefix + command_text)} {self.syntax}"
                    )
                else:
                    syntax = self.syntax.split("\n")
                    for syn in syntax:
                        error_message = error_message + f"\n<emoji id=\"5463258057607760727\">🩸</emoji>{escape(prefix + command_text)} {syn}"
                error_message = error_message + (
                    f"\n"
                    f"\n<emoji id=\"5341633328338451873\">❗</emoji>Вы написали:</b>"
                    f"\n<emoji id=\"5463258057607760727\">🩸</emoji><code>{escape(prefix + command_text)}</code>"
                )
            else:
                error_message = (
                    f"E R R O R"
                    f"\n❗️{escape(e)}"
                    f"\n"
                    f"\n❗️Команда должна выглядеть так:"
                )
                if len(self.syntax.split("\n")) == 1:
                    error_message = (
                        f"\n❤️{escape(prefix + command_text)} {self.syntax}"
                    )
                else:
                    syntax = self.syntax.split("\n")
                    for syn in syntax:
                        error_message = error_message + f"\n❤️{escape(prefix + command_text)} {syn}"
                error_message = error_message + (
                    f"\n"
                    f"\n❗️Вы написали:"
                    f"\n❤️<code>{escape(prefix + command_text)}</code>"
                )
            await self.client.send_message(message.chat.id, error_message, parse_mode=enums.ParseMode.HTML)