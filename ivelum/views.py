import re
from bs4 import BeautifulSoup, NavigableString

import requests
from django.http import HttpResponse

from ivelum.constants import TARGET_URL, PROXY, TARGET, TARGET_LINK
from ivelum.url_parser import StrUrlParser, RequestUrlParser


class ProxyClient:

    def __init__(self, initial_request, replaced_url):
        self.__url = replaced_url
        self.__method = initial_request.method.lower()

    def get_response(self):
        return getattr(requests, self.__method)(self.__url).content


class ResponseProcessor:

    def __init__(self, soup_response):
        self.__soup_response = soup_response

    def get_result(self, *args, **kwargs):
        tags = self.__soup_response.find_all(['link', 'img', 'script', 'a'])
        for tag in tags:
            if tag.name == 'link' and tag.get('rel') == ['stylesheet']:
                self.add_target_url_to_tag(tag, 'href')
            elif tag.name == 'a':
                self.replace_href_by_proxy(tag)
            elif tag.name == 'img' or tag.name == 'script':
                self.add_target_url_to_tag(tag, 'src')
        comment_divs = self.__soup_response.find_all('div', class_='comment')
        for comment_div in comment_divs:
            if comment_div is not None:
                self.modify_content(comment_div)
        return str(self.__soup_response.prettify())

    @staticmethod
    def add_target_url_to_tag(tag, replaced_tag):
        tag[replaced_tag] = TARGET_URL + tag[replaced_tag]

    @staticmethod
    def replace_href_by_proxy(tag):
        parsed_url = StrUrlParser(tag['href'])
        if parsed_url.netloc in [TARGET_LINK, TARGET]:
            parsed_url.netloc = PROXY
            tag['href'] = parsed_url.parsed_url

    def modify_content(self, tag):
        """Check all nested NavigableString objects,
        split by space and optional proceeding punctuation symbols and add '™' mark for 6-length words
        """
        if isinstance(tag, NavigableString):
            words = [word + '™' if len(word) == 6 and word.isalpha() else word for word in
                     re.split(r'([,.!:;]\s+|[,.!:;]$|\s+)', tag)]
            tag.replace_with(''.join(words))
        children = [] if not hasattr(tag, 'children') else tag.children
        for child in children:
            self.modify_content(child)


def proxy_view(request):
    input_url_request_parser = RequestUrlParser(request)
    input_url_request_parser.netloc = TARGET
    proxy_client = ProxyClient(request, input_url_request_parser.parsed_url)
    soup = BeautifulSoup(proxy_client.get_response(), 'html.parser')
    modified_content = ResponseProcessor(soup)
    return HttpResponse(modified_content.get_result())
