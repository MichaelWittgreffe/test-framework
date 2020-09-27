from typing import Dict, Any

from generic_api.request_runner import RequestRunner


class ExampleRequestRunner(RequestRunner):
    "example class for another implementation in the future"

    def __init__(self, auth_url: str = "", username: str = "", password: str = ""):
        "constructor - must call super, any additional fields can be initialized here"
        super().__init__(auth_url=auth_url, username=username, password=password)

    def authenticate(self) -> str:
        """
        Method for authenticating with the configured authentication schema - derived classes should override this
        Must return a string authentication token.
        """
        return ""

    def set_request_token(self, request_headers: Dict[str, Any], auth_token: str) -> Dict[str, Any]:
        """
        Method to set the authentication token in the request headers.
        Should be overridden by derived classes
        Must return the expected request header as a dict, with the authentication token set.
        """
        return {}
