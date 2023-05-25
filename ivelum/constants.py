import sys

from urllib.parse import urlunparse
from frozendict import frozendict

TARGET = 'news.ycombinator.com'
TARGET_LINK = 'www.ycombinator.com'
PROXY = ':'.join(['127.0.0.1', sys.argv[-1]])
SCHEMAS = frozendict({TARGET: 'https', PROXY: 'http'})
TARGET_URL = urlunparse((SCHEMAS.get(TARGET), TARGET, '', '', '', '')) + '/'
