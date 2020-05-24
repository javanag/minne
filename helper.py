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


def setup_mumble_profile(mumble_client, config):
    '''Mute and deafen self, set informative comment.'''
    minne_user = mumble_client.users.myself
    minne_channel = mumble_client.channels[minne_user['channel_id']]

    comment_message = \
        f"Recording chat history in channel: <b>{minne_channel['name']}</b>"\
        "<br />When you rejoin this channel, I'll send the last"\
        f" {config.chat_history_day_count} days of chats to you privately."

    minne_user.deafen()
    minne_user.comment(comment_message)
