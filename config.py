import os

class Config:
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', None)
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

    if LINE_CHANNEL_SECRET is None:
        raise ValueError('Specify LINE_CHANNEL_SECRET as an environment variable.')
    if LINE_CHANNEL_ACCESS_TOKEN is None:
        raise ValueError('Specify LINE_CHANNEL_ACCESS_TOKEN as an environment variable.')
