import json
import logging
from json import JSONDecodeError

logging.basicConfig()
logger = logging.getLogger(__name__)

with open('../settings.json', 'r') as f:

    try:
        settings = json.load(f)
    except JSONDecodeError as e:
        logger.warning(f'Please check settings.json. Exept: {e}')
        exit(1)

    API_ID = settings['api_id']
    API_HASH = settings['api_hash']
    CHATS = []

    CM = settings['channels_mapping']
    CHANNEL_MAPPING = {}
    if CM is not None:
        for match in CM:
            sources = match['sources']
            targets = match['targets']
            settings_mapping = match['settings']
            try:
                settings_mapping['white_list']
            except KeyError:
                settings_mapping['white_list'] = []
            try:
                settings_mapping['black_list']
            except KeyError:
                settings_mapping['black_list'] = []
            try:
                settings_mapping['replace']
            except KeyError:
                settings_mapping['replace'] = []
            for source in sources:
                CHANNEL_MAPPING.setdefault(
                    source, []).extend([targets, settings_mapping])
        CHATS = list(CHANNEL_MAPPING.keys())

    TIMEOUT_MIRRORING = settings['timeout_mirroring']
    LIMIT_TO_WAIT = 50
    # auth session string: can be obtain by run login.py
    SESSION_STRING = settings['session_string']
    DB_NAME = settings['db_name']
    DB_FILE_NAME = settings['db_file_name']
    LOG_LEVEL = settings['log_level']
