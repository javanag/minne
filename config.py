import os


class Configuration():
    '''Configuration object to store settings and env. variables.'''

    def __init__(self):
        self.mumble_username = os.getenv('MUMBLE_USERNAME', 'minne')
        self.mumble_server_host = os.environ['MUMBLE_SERVER_HOST']
        self.mumble_server_port = os.getenv('MUMBLE_SERVER_PORT', '64738')
        self.mumble_server_password = os.getenv('MUMBLE_SERVER_PASSWORD', '')

        self.certfile_path = os.getenv('MUMBLE_CERTFILE_PATH')
        self.keyfile_path = os.getenv('MUMBLE_KEYFILE_PATH')
        self.reconnect = True
        self.loop_rate = 0.1

        self.mumble_application_string = os.getenv(
            'MUMBLE_APPLICATION_STRING',
            f'{self.mumble_username}_bot')
        self.db_connection_url = os.environ['DB_CONNECTION_URL']
        self.chat_history_day_count = int(
            os.environ.get('CHAT_HISTORY_DAY_COUNT', 7))
