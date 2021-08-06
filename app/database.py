import os
import sqlite3
import logging

logger = logging.getLogger(__name__)


class Database:

    def __init__(self, db_name: str, db_file_name: str):
        self.db_name = db_name
        self.db_file_name = db_file_name
        if not os.path.isfile(f'../db/{db_file_name}.db'):
            os.makedirs("../db", exist_ok=True)
            self.__create_table()

    def __db(self, query: str):
        try:
            sqlite_connection = sqlite3.connect(
                f'../db/{self.db_file_name}.db', timeout=60)
            cursor = sqlite_connection.cursor()
            cursor.execute(query)
            sqlite_connection.commit()
            total_rows = cursor.fetchall()
            cursor.close()
            return total_rows

        except sqlite3.Error as error:
            logger.error(error, exc_info=True)
        finally:
            if (sqlite_connection):
                sqlite_connection.close()

    def __create_table(self):
        query_create_table = f'''CREATE TABLE IF NOT EXISTS {self.db_name} (
                                      id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                      original_id INTEGER NOT NULL,
                                      original_channel INTEGER NOT NULL,
                                      mirror_id INTEGER NOT NULL,
                                      mirror_channel INTEGER NOT NULL);'''

        query_create_index = f'''CREATE INDEX IF NOT EXISTS index_original ON {self.db_name}(
                                      original_id, original_channel);'''
        self.__db(query_create_table)
        self.__db(query_create_index)
        logger.info('SQLite table was created')

    def insert(self, original_id: int, original_channel: int, mirror_id: int, mirror_channel: int):
        query = f'''INSERT INTO {self.db_name}
                                  (original_id, original_channel,
                                   mirror_id, mirror_channel)
                                  VALUES ({original_id}, {original_channel}, {mirror_id}, {mirror_channel});'''
        self.__db(query)

    def find_by_original_id(self, original_id: int, original_channel: int):
        query = f'''SELECT original_id, original_channel, mirror_id, mirror_channel
                                FROM {self.db_name}
                                WHERE original_id = {original_id}
                                AND original_channel = {original_channel}
                                '''
        return self.__db(query)
