# config.py

import os

# LINE Credentials
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', None)
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if CHANNEL_SECRET is None:
    print('Specify LINE_CHANNEL_SECRET as an environment variable.')
    sys.exit(1)

if CHANNEL_ACCESS_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as an environment variable.')
    sys.exit(1)
