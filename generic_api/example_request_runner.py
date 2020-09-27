from .base_request_runner import RequestRunner


class ExampleRequestRunner(RequestRunner):
    "example class for another implementation in the future"

    def __init__(self, auth_url='', username='', password=''):
        "constructor - must call super(), any additional fields can be initialized here"
        super(ExampleRequestRunner, self).__init__(auth_url=auth_url, username=username, password=password)

    def authenticate(self):
        "this is where the example authentication method will be implemented"
        authentication_token = ""
        return authentication_token

    def set_request_token(self, request_headers, auth_token):
        "this is where the example auth token is set against any HTTP request headers"
        new_request_header = {}
        return new_request_header
