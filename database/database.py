class DataBase:
    def __init__(self, database_path: str):
        pass

    def save_log(self, user_id, chat_id, text, is_audio, is_file, command, result):
        pass

    def get_user_story(self, user_id, chat_id):
        pass

    def get_user_last_query(self, user_id, chat_id):
        pass
