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
    command = "command"
    description = ""
    syntax = f"{escape("<edit>")} <Старое название> <Новое название>"
    def __init__(self, *args):
        super().__init__(*args)

    async def main(self, command_text, command_name, command_args, prefix, message):
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


