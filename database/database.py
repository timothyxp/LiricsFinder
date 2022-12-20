from tinydb import TinyDB, Query
from datetime import datetime


class DataBase:
    def __init__(self, database_path: str):
        self.db = TinyDB(database_path)
        self.user = Query()

    def save_log(self, user_id, chat_id, text, is_audio, is_file, command, result):
        dt = datetime.now()
        dt_str = datetime.strptime(str(dt)[:-7], '%Y-%m-%d %H:%M:%S')
        self.db.insert({'user_id': user_id, 'chat_id': chat_id, 'text': text, 'is_audio': is_audio, 'is_file': is_file,\
                        'command': command, 'result': result, 'date_time': dt_str})

    def get_user_story(self, user_id):
        return self.db.search(self.user.user_id == user_id)

    def get_user_last_query(self, user_id, chat_id):
        return self.db.search(self.user.user_id == user_id and self.user.chat_id == chat_id)[-1]
