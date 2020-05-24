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
