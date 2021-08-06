import logging
import time

from telethon import events
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.tl.types import InputMediaPoll, MessageMediaPoll, MessageEntityTextUrl

from database import Database
from settings import (API_HASH, API_ID, CHANNEL_MAPPING, CHATS,
                      LIMIT_TO_WAIT, LOG_LEVEL, SESSION_STRING,
                      TIMEOUT_MIRRORING, DB_NAME, DB_FILE_NAME)
from utils import check_list, replace_text

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(level=LOG_LEVEL)


client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
db = Database(DB_NAME, DB_FILE_NAME)


@client.on(events.Album(chats=CHATS))
async def handler_album(event):
    """Album event handler.
    """
    try:
        logger.debug(f'New Album from {event.chat_id}:\n{event}')
        targets = CHANNEL_MAPPING.get(event.chat_id)[0]
        if targets is None or len(targets) < 1:
            logger.warning(f'Album. No target channel for {event.chat_id}')
            return
        # media
        files = []
        # captions
        caps = []
        # original messages ids
        original_idxs = []
        for item in event.messages:
            files.append(item.media)
            caps.append(item.message)
            original_idxs.append(item.id)
        sent = 0
        for chat in targets:
            mirror_messages = await client.send_file(chat, caption=caps, file=files)
            if mirror_messages is not None and len(mirror_messages) > 1:
                for idx, m in enumerate(mirror_messages):
                    db.insert(original_idxs[idx],
                              event.chat_id,
                              m.id,
                              chat)
            sent += 1
            if sent > LIMIT_TO_WAIT:
                sent = 0
                time.sleep(TIMEOUT_MIRRORING)
    except Exception as e:
        logger.error(e, exc_info=True)


@client.on(events.NewMessage(chats=CHATS))
async def handler_new_message(event):
    """NewMessage event handler.
    """
    # skip if Album
    if hasattr(event, 'grouped_id') and event.grouped_id is not None:
        return
    try:
        logger.debug(f'New message from {event.chat_id}:\n{event.message}')
        targets = CHANNEL_MAPPING.get(event.chat_id)[0]
        settings = CHANNEL_MAPPING.get(event.chat_id)[1]
        if targets is None or len(targets) < 1:
            logger.warning(
                f'NewMessage. No target channel for {event.chat_id}')
            return
        if len(settings['white_list']) > 0:
            if check_list(settings['white_list'], event.message.message) is False:
                return
        if len(settings['black_list']) > 0:
            if check_list(settings['black_list'], event.message.message) is True:
                return
        if len(settings['replace']) > 0:
            event.message.message = replace_text(
                settings['replace'], event.message.message)
        sent = 0
        for chat in targets:
            mirror_message = None
            if isinstance(event.message.media, MessageMediaPoll):
                mirror_message = await client.send_message(chat,
                                                           file=InputMediaPoll(poll=event.message.media.poll))
            else:
                mirror_message = await client.send_message(chat, event.message)

            if mirror_message is not None:
                db.insert(event.message.id,
                          event.chat_id,
                          mirror_message.id,
                          chat)
            sent += 1
            logger.info(
                f'{chat}, {mirror_message.id} was created')
            if sent > LIMIT_TO_WAIT:
                sent = 0
                time.sleep(TIMEOUT_MIRRORING)

    except Exception as e:
        logger.error(e, exc_info=True)


@ client.on(events.MessageEdited(chats=CHATS))
async def handler_edit_message(event):
    """MessageEdited event handler.
    """
    try:
        logger.debug(f'Edit message {event.message.id} from {event.chat_id}')
        targets = db.find_by_original_id(event.message.id, event.chat_id)
        settings = CHANNEL_MAPPING.get(event.chat_id)[1]
        if targets is None or len(targets) < 1:
            logger.warning(
                f'MessageEdited. No target channel for {event.chat_id}')
            return
        if len(settings['white_list']) > 0:
            if check_list(settings['white_list'], event.message.message) is False:
                return
        if len(settings['black_list']) > 0:
            if check_list(settings['black_list'], event.message.message) is True:
                return
        if len(settings['replace']) > 0:
            event.message.message = replace_text(
                settings['replace'], event.message.message)
        sent = 0
        for chat in targets:
            await client.edit_message(chat[3], chat[2], event.message.message)
            sent += 1
            logger.info(
                f'{chat[3]}, {chat[2]} was edited')
            if sent > LIMIT_TO_WAIT:
                sent = 0
                time.sleep(TIMEOUT_MIRRORING)
    except Exception as e:
        logger.error(e, exc_info=True)


if __name__ == '__main__':
    client.start()
    if client.is_user_authorized():
        me = client.get_me()
        logger.info(f'Connected as {me.username} ({me.phone})')
        client.run_until_disconnected()
    else:
        logger.error('Cannot be authorized')
