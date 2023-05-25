from abc import ABC
from urllib.parse import urlencode, urlunparse, urlparse

from ivelum.constants import SCHEMAS


class BaseUrlParser(ABC):
    _url_parameters = ('scheme', 'netloc', 'path', 'params', 'query', 'fragment', )
    _scheme_map = SCHEMAS
    _netloc: str
    fragment = ''
    params = ''

    @property
    def parsed_url(self):
        return urlunparse([getattr(self, attr) for attr in self._url_parameters])

    @property
    def netloc(self):
        return self._netloc

    @netloc.setter
    def netloc(self, value):
        self._netloc = value

    @property
    def scheme(self):
        return self._scheme_map.get(self._netloc, '')


class RequestUrlParser(BaseUrlParser):

    def __init__(self, request, **kwargs):
        super().__init__(**kwargs)
        self.netloc = request.get_host()
        self.path = request.path_info
        query_params = getattr(request, request.method)
        self.query = urlencode(query_params) if query_params else ''


class StrUrlParser(BaseUrlParser):

    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)
        parsed_url = urlparse(url)
        for attr in self._url_parameters[1:]:
            setattr(self, attr, getattr(parsed_url, attr))
