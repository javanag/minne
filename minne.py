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
    '''Callback prints message history to user upon joining server.
    
    Due to official Mumble client truncating messages that would take up a
    larger area than 2048^2 px, estimate the area of the rectangle generated
    assuming all text is 32px font. To account for larger HTML text like the h1
    tag.

    One this area limit is reached, send the message, and continue to accrue
    and calculate area of messages until there are none remaining that fall
    within the configured chat history window.
    '''
    MAX_MUMBLE_CLIENT_MESSAGE_AREA = 4194304
    ESTIMATED_MUMBLE_FONT_SIZE_PX = 32

    channel = mumble_client.channels[user['channel_id']]

    today = datetime.datetime.now()
    response_cutoff_date = today - datetime.timedelta(
        days=chat_history_day_count)

    records = session.query(
        Message
    ).filter(
        Message.timestamp >= response_cutoff_date
    ).filter_by(
        channel_name=channel['name']
    ).order_by(
        Message.timestamp
    ).all()

    formatted_messages = []
    max_message_line_width = 0

    for message in records:
        formatted_message = format_message(user['name'], message)
        message_line_width = len(formatted_message)
        if message_line_width >= max_message_line_width:
            max_message_line_width = message_line_width

        message_line_height = (len(formatted_messages) + 1)
        total_message_area = max_message_line_width * \
            message_line_height * \
            ESTIMATED_MUMBLE_FONT_SIZE_PX

        if total_message_area < MAX_MUMBLE_CLIENT_MESSAGE_AREA:
            formatted_messages.append(formatted_message)
        else:
            user.send_text_message(
                f"<br />{'<br />'.join(formatted_messages)}")
            formatted_messages = []

            max_message_line_width = message_line_width
            formatted_messages.append(formatted_message)
            time.sleep(0.2)

    user.send_text_message(f"<br />{'<br />'.join(formatted_messages)}")


def format_message(user_name, message_record):
    timestamp_string = \
        "<span class=\"log-time\">["\
        f"{message_record.timestamp.strftime('%H:%M:%S')}"\
        "]</span>"

    if user_name == message_record.user_name:
        sender_string = \
            'To <span class="log-channel">'\
            f'{message_record.channel_name}</span>:'
    else:
        sender_string = \
            '<b><span class="log-source">'\
            f'{message_record.user_name}</span></b>:'

    formatted_message = \
        f'{timestamp_string} {sender_string} {message_record.message}'
    return formatted_message


def on_message(message):
    '''Callback stores messages in same channel to database upon reception .'''
    try:
        channel_id = message.channel_id.pop()
    except IndexError:
        # No channel_id means it's a private message, skip for now
        return

    channel = mumble_client.channels[channel_id]
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
