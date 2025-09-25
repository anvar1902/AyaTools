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
    command = "prefix"
    description = ""
    syntax = f"{escape("<add/remove/list>")} <префикс>"
    def __init__(self, *args):
        super().__init__(*args)

    async def main(self, command_text, command_name, command_args, prefix, message):
        if not len(command_args) < 1:
            operation = command_args[0]
            if not len(command_args) < 2:
                new_prefix = command_args[1]
                if operation == "add":
                    if not new_prefix in self.spec.prefixs:
                        self.spec.prefixs.append(new_prefix)
                        await self.client.send_message(message.chat.id, f"Префикс {new_prefix} успешно добавлен✅")
                    else:
                        raise ValueError("Данный префикс уже существует")
                elif operation == "remove":
                    if new_prefix in self.spec.prefixs:
                        if len(self.spec.prefixs) > 1:
                            self.spec.prefixs.remove(new_prefix)
                            await self.client.send_message(message.chat.id, f"Префикс {new_prefix} успешно удалён✅")
                        else:
                            raise ValueError("У вас всего 1 префикс, вы не можете его удалить, добавьте ещё префиксы чтобы удалить этот")
                    else:
                        raise ValueError("Данного префикса не существует")
            elif operation == "list":
                result = '\n'.join(pref for pref in self.spec.prefixs)
                await self.client.send_message(message.chat.id, f"Список префиксов: \n{result}")
            else:
                raise ValueError("Такой операции не существует")
        else:
            raise ValueError("Недостаточно аргументов")


