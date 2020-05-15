from config import Configuration
from models import Base
from models import Message
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
import pymumble_py3 as pymumble
import time
import datetime

mumble_client = None
session = None
chat_history_day_count = None


def main():
    global mumble_client
    config = Configuration()

    global chat_history_day_count
    chat_history_day_count = config.chat_history_day_count

    engine = create_engine(config.db_connection_url, echo=True)
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)  # Create all tables if necessary
    Session = sessionmaker(bind=engine)

    global session
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
        pymumble.constants.PYMUMBLE_CLBK_USERCREATED, on_user_join)
    mumble_client.callbacks.set_callback(
        pymumble.constants.PYMUMBLE_CLBK_TEXTMESSAGERECEIVED, on_message)

    while True:
        time.sleep(1)


def on_user_join(user, message=None):
    '''Callback prints message history to user upon joining server.'''
    channel = mumble_client.channels[user['channel_id']]

    today = datetime.datetime.now()
    response_cutoff_date = today - datetime.timedelta(
        days=chat_history_day_count)

    # TODO: Please clean ALL of the following up.
    records = session.query(Message)\
        .filter(Message.timestamp >= response_cutoff_date)\
        .filter_by(channel_name=channel['name'])\
        .order_by(Message.timestamp).all()

    formatted_messages = []
    for message in records:
        if message.user_name == user['name']:
            user_section = f"To <span class=\"log-channel\">{channel['name']}</span>: "
        else:
            user_section = f"<b><span class=\"log-source\">{message.user_name}</span></b>: "

        formatted_messages.append(
            f"<span class=\"log-time\">[{message.timestamp.strftime('%H:%M:%S')}]</span> "
            f"{user_section}{message.message}"
        )

    message_history = '<br />'.join(formatted_messages)
    user.send_text_message(
        f"History of channel <span class=\"log-channel\">{channel['name']}</span>:<br />{message_history}")


def on_message(message):
    '''Callback stores messages in same channel to database upon reception .'''
    channel = mumble_client.channels[message.channel_id.pop()]
    user = mumble_client.users[message.actor]
    message_text = message.message

    message_record = Message(
        user_name=user['name'],
        channel_name=channel['name'],
        message=message_text,
        timestamp=datetime.datetime.now())

    session.add(message_record)
    session.commit()


if __name__ == '__main__':
    main()
