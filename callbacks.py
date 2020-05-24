from helper import format_message
from models import Message
from tidylib import tidy_fragment
import datetime


def create_on_message_callback(mumble_client, session):
    '''Create closure with references to client and sqlalchemy session.

    Callback stores messages in same channel to database upon reception.
    '''

    def on_message(message):
        try:
            channel_id = message.channel_id.pop()
        except IndexError:
            # No channel_id means it's a private message, skip for now
            return

        channel = mumble_client.channels[channel_id]
        user = mumble_client.users[message.actor]
        message_text = message.message

        html_linted_message_text, _ = tidy_fragment(message_text)

        message_record = Message(
            user_name=user['name'],
            channel_name=channel['name'],
            message=html_linted_message_text,
            timestamp=datetime.datetime.now())

        session.add(message_record)
        session.commit()

    return on_message


def create_on_user_join_callback(mumble_client, session, config):
    '''Create closure with references to client, sqlalchemy session, and config

    Callback prints message history to user upon joining server.

    Due to official Mumble client truncating messages that would take up a
    larger area than 2048^2 px, estimate the area of the rectangle generated
    assuming all text is 32px font. To account for larger HTML text like the h1
    tag.

    One this area limit is reached, send the message, and continue to accrue
    and calculate area of messages until there are none remaining that fall
    within the configured chat history window.
    '''

    def on_user_join(user, message=None):
        MAX_MUMBLE_CLIENT_MESSAGE_AREA = 4194304
        ESTIMATED_MUMBLE_FONT_SIZE_PX = 32

        channel = mumble_client.channels[user['channel_id']]

        today = datetime.datetime.now()
        response_cutoff_date = today - datetime.timedelta(
            days=config.chat_history_day_count)

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
        previous_message_date = None

        for message in records:
            current_message_date = message.timestamp.date()
            if not previous_message_date or \
                    not (previous_message_date == current_message_date):

                date_change_line = \
                    '<h3 class=\"log-time\">['\
                    f"{current_message_date.strftime('%a %B %d %Y')}"\
                    ']</h3>'
                date_change_line_width = len(date_change_line)
                if date_change_line_width >= max_message_line_width:
                    max_message_line_width = date_change_line_width

                # TODO: Fix the following code duplication later
                message_line_height = (len(formatted_messages) + 1)
                total_message_area = max_message_line_width * \
                    message_line_height * \
                    ESTIMATED_MUMBLE_FONT_SIZE_PX

                if total_message_area < MAX_MUMBLE_CLIENT_MESSAGE_AREA:
                    formatted_messages.append(date_change_line)
                else:
                    user.send_text_message(
                        f"<br />{'<br />'.join(formatted_messages)}")
                    formatted_messages = [date_change_line]
                    max_message_line_width = date_change_line_width

            formatted_message = format_message(user['name'], message)

            # Send image messages individually due to lower space predictability
            if '<img' in formatted_message:
                user.send_text_message(
                    f"<br />{'<br />'.join(formatted_messages)}")
                formatted_messages = []
                max_message_line_width = 0

                user.send_text_message(f"<br />{formatted_message}")
                continue

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
            previous_message_date = current_message_date

        user.send_text_message(f"<br />{'<br />'.join(formatted_messages)}")

    return on_user_join
