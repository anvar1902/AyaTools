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
    command = "help"
    description = ""
    syntax = f"<Команда>"
    def __init__(self, *args):
        super().__init__(*args)

    async def main(self, command_text, command_name, command_args, prefix, message):
        if not len(command_args) < 1:
            c_name = command_args[0]
            if c_name in self.spec.commands.keys():
                c_obj = self.spec.commands[c_name]
                help_text = (
                    "Подсказка по команде:"
                    f"\n{prefix}{c_name} {c_obj.syntax}"
                    f"\n{c_obj.description}"
                )
                await self.client.send_message(message.chat.id, help_text)
            else:
                raise ValueError("Такой команды не существует")
        else:
            help_text = "Список всех команд:"
            for c_name, _ in self.spec.commands.items():
                help_text = help_text + f"\n{prefix}{c_name}"
            await self.client.send_message(message.chat.id, help_text)


