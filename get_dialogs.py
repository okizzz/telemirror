from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from app.settings import (API_HASH, API_ID, SESSION_STRING)
from telethon.tl.types import PeerChannel


def do_full_copy():
    with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        for dialog in client.get_dialogs():
            if not isinstance(dialog.message.peer_id, PeerChannel):
                continue
            try:
                print("++++++++++++++++++++++++++++++++")
                print(f'channel_id: {str(dialog.entity.id)}')
                print(f'dialog_id: -100{str(dialog.entity.id)}')
                print(f'title: {str(dialog.entity.title)}')
                print(f'username: @ {str(dialog.entity.username)}')
                print(f'creator: {str(dialog.entity.creator)}')
                print("++++++++++++++++++++++++++++++++")
                print("")
            except Exception as e:
                print(e)


if __name__ == "__main__":
    do_full_copy()
