from config import Configuration
from models import Base
from sqlalchemy import create_engine
from sqlalchemy_utils import (
    database_exists,
    create_database
)
from sqlalchemy.orm import sessionmaker
import pymumble_py3 as pymumble
import time
from callbacks import (
    create_on_message_callback,
    create_on_user_join_callback
)


def main():
    config = Configuration()

    engine = create_engine(config.db_connection_url, echo=True)
    if not database_exists(engine.url):
        create_database(engine.url)

    Base.metadata.create_all(engine)  # Create all tables if necessary
    Session = sessionmaker(bind=engine)
    session = Session()

    mumble_client = pymumble.Mumble(
        host=config.mumble_server_host,
        user=config.mumble_username,
        password=config.mumble_server_password,
        certfile=config.certfile_path,
        keyfile=config.keyfile_path,
        reconnect=config.reconnect)
    mumble_client.set_application_string(config.mumble_application_string)
    mumble_client.set_loop_rate(config.loop_rate)

    mumble_client.start()
    mumble_client.is_ready()

    mumble_client.callbacks.add_callback(
        pymumble.constants.PYMUMBLE_CLBK_USERCREATED,
        create_on_user_join_callback(mumble_client, session, config)
    )
    mumble_client.callbacks.set_callback(
        pymumble.constants.PYMUMBLE_CLBK_TEXTMESSAGERECEIVED,
        create_on_message_callback(mumble_client, session)
    )

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
