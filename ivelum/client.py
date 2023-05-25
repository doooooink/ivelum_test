import requests


class ProxyClient:

    def __init__(self, initial_request, replaced_url):
        self.__url = replaced_url
        self.__initial_request = initial_request
        self.__method = initial_request.method.lower()

    def get_response(self):
        return getattr(requests, self.__method)(self.__url)
