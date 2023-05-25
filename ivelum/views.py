from ivelum.client import ProxyClient
from ivelum.constants import TARGET
from ivelum.response_processor import response_processor_factory
from ivelum.url_parser import RequestUrlParser


def proxy_view(request):
    input_url_request_parser = RequestUrlParser(request)
    input_url_request_parser.netloc = TARGET
    proxy_client = ProxyClient(request, input_url_request_parser.parsed_url)
    proxy_client_response = proxy_client.get_response()
    response_processor = response_processor_factory(proxy_client_response, request.META['SERVER_PORT'])
    return response_processor.processed_response()
