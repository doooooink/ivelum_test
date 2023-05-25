import re
from abc import ABC, abstractmethod

from bs4 import NavigableString, BeautifulSoup
from django.http import HttpResponse
from requests import Response

from ivelum.constants import TARGET_LINK, TARGET, PROXY
from ivelum.url_parser import StrUrlParser


class BaseProcessorProtocol(ABC):

    @abstractmethod
    def processed_response(self) -> HttpResponse:
        pass


class HtmlResponseProcessor(BaseProcessorProtocol):

    def __init__(self, response: Response, local_port, *args, **kwargs):
        self._response = response
        self._content_type = response.headers.get('content-type')
        self._soup = BeautifulSoup(response.content, 'html.parser')
        self._local_port = local_port

    def processed_response(self):
        for top_level_tag in self._soup.find_all(recursive=False):
            if top_level_tag is not None:
                self.modify_content_recursively(top_level_tag)
        return HttpResponse(self._soup.prettify(), content_type=self._content_type)

    def modify_content_recursively(self, tag):
        """Check all nested tags and apply transformations for them"""
        if tag.name == 'a' and tag.has_attr('href'):
            self.replace_href_by_proxy(tag)
        if isinstance(tag, NavigableString):
            self.modify_string(tag)
        children = [] if not hasattr(tag, 'children') else tag.children
        for child in children:
            self.modify_content_recursively(child)

    def replace_href_by_proxy(self, tag):
        parsed_url = StrUrlParser(tag['href'])
        if parsed_url.netloc in [TARGET_LINK, TARGET]:
            parsed_url.netloc = ':'.join([PROXY, self._local_port])
            tag['href'] = parsed_url.parsed_url

    @staticmethod
    def modify_string(tag):
        """Split string by space, `"` symbol, and optional proceeding punctuation symbols
        and add '™' mark for 6-length words"""
        words = [word + '™' if len(word) == 6 and word.isalpha() else word for word in
                 re.split(r'([,.!:;]\s+|[,.!:;]$|\s+|")', tag)]
        tag.replace_with(''.join(words))


class MediaResponseProcessor(BaseProcessorProtocol):

    def __init__(self, response: Response, *args, **kwargs):
        self._response = response
        self._content_type = response.headers.get('content-type')

    def processed_response(self):
        return HttpResponse(self._response.content, content_type=self._content_type)


RESPONSE_PROCESSORS_MAP = {
    'image/gif': MediaResponseProcessor,
    'image/svg+xml': MediaResponseProcessor,
    'image/x-icon': MediaResponseProcessor
}


def response_processor_factory(response: Response, local_port) -> BaseProcessorProtocol:
    return RESPONSE_PROCESSORS_MAP.get(
        response.headers.get('content-type'), HtmlResponseProcessor
    )(response, local_port)
