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
    command = "stop"
    description = ""
    syntax = f"<сообщение>"
    def __init__(self, *args):
        super().__init__(*args)

    async def main(self, command_text, command_name, command_args, prefix, message):
        if not len(command_args) < 1:
            for spammer_obj in self.spec.tasks["spam"]:
                if spammer_obj.data["text"] == command_args[0]:
                    if spammer_obj.data["chat_id"] == message.chat.id:
                        await spammer_obj.stop()
        else:
            raise ValueError("Недостаточно аргументов")