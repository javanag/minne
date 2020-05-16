# Minne

A Mumble bot that will remind you of conversations past. Upon connection to the server, a configurable time period of chat history in the joining user's channel will be privately sent to them as a formatted HTML text message, that mimics the style of the normal Mumble client UI.

## Setup

### Dependencies

In addition to installing the pip packages:
`python3 -m pip install -r requirements.txt`

Some pip packages rely on OS libraries. Look for and install `libopus` and `tidy` (HTML reformatter) via your OS's package manager.

### Connections

Point Minne to a Mumble server, and to a database by using the [SQLAlchemy URL](https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls) format of: `dialect+driver://username:password@host:port/database`, via the environment variables in the following section.

### Environment variables

Mandatory:

```
DB_CONNECTION_URL
MUMBLE_SERVER_HOST
```

Optional to set (defaults are chosen/generated in config.py):

```
CHAT_HISTORY_DAY_COUNT
MUMBLE_APPLICATION_STRING
MUMBLE_CERTFILE_PATH
MUMBLE_KEYFILE_PATH
MUMBLE_SERVER_PASSWORD
MUMBLE_SERVER_PORT
MUMBLE_USERNAME
```

## Limitations

Currently bot only listens and records messages in it's current channel, or also possibly if it is shouted at.
