from urllib.parse import urlunparse
from frozendict import frozendict

TARGET = 'news.ycombinator.com'
TARGET_LINK = 'www.ycombinator.com'
PROXY = 'localhost'
SCHEMAS = frozendict({TARGET: 'https', PROXY: 'http'})
TARGET_URL = urlunparse((SCHEMAS.get(TARGET), TARGET, '', '', '', '')) + '/'
