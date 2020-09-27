import requests
import json
from typing import Dict, Callable, Any, Tuple, Optional


class RequestRunner():
    """
    Base class for executing generic HTTP/1.1 requests
    To derive from this class you must implement the 'authenticate' and 'set_request_token' methods
        if you just to run no-auth requests you can use the base class
    """

    def __init__(self, auth_url: str = "", username: str = "", password: str = ""):
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.supported_methods: Dict[str, Callable] = {
            "GET": self._get_request,
            "POST": self._post_request,
            "DELETE": self._delete_request,
            "PUT": self._put_request,
        }
        self.supported_content_types: Dict[str, Dict[str, Callable]] = {
            "application/json": {
                "encode": self._encode_data_to_json,
                "decode": self._decode_json_to_data,
            },
            "application/json; charset=UTF-8": {
                "encode": self._encode_data_to_json,
                "decode": self._decode_json_to_data,
            }
        }

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

    def run_request(self, method: str, url: str, content_type: str = "", body: Dict[str, Any] = {}, query_params: Dict[str, Any] = {},
                    header_params: Dict[str, Any] = {}, authenticate: bool = True) -> Tuple[dict, dict, int]:
        "run an HTTP/1.1 request"
        if not len(method) or method not in self.supported_methods:
            raise ValueError(f"Method {method} Not Supported Or Invalid")
        if not len(url):
            raise ValueError("Invalid URL")

        runner: Callable = self.supported_methods[method.upper()]
        runner_kwargs = {
            "url": url,
            "content_type": content_type,
            "body": body,
            "query_params": query_params,
            "header_params": header_params,
        }

        if authenticate:
            if not len(self.auth_url) or not len(self.username) or not len(self.password):
                raise ValueError("Authentication Details Not Populated")

            auth_token = self.authenticate()

            if not len(auth_token):
                raise ValueError("Returned Auth Token Is Empty")

            runner_kwargs["auth_token"] = auth_token

        return runner(**runner_kwargs)

    def _encode_request_body(self, content_type: str, request_data: Dict[str, Any]) -> str:
        "encodes and returns the body for the request if the content_type is supported"
        if request_data is None:
            raise ValueError("request_data Is None")

        if content_type not in self.supported_content_types:
            raise ValueError(f"Unsupported Content Type: {content_type}")

        type_data = self.supported_content_types[content_type]
        encoder = type_data['encode']
        return encoder(request_data)

    def _decode_response_body(self, resp_content_type: str, resp_data: str) -> Dict[str, Any]:
        "decodes a response body from the returned MIME type to a Python data structure"
        if resp_content_type not in self.supported_content_types:
            raise ValueError(f"Response Content-Type Is Not Supported: {resp_content_type}")

        type_data = self.supported_content_types[resp_content_type]
        decoder = type_data['decode']
        return decoder(resp_data)

    def _encode_data_to_json(self, data: Dict[str, Any]) -> str:
        "encodes the given dict to a json string"
        try:
            return json.dumps(data)
        except Exception as ex:
            raise ValueError(f"Ex Dumps JSON: {data}")

    def _decode_json_to_data(self, raw_json: str) -> Dict[str, Any]:
        "decodes the given json string to a dict"
        try:
            return json.loads(raw_json)
        except Exception as ex:
            raise ValueError(f"Ex Decoding JSON: {str(ex)}")

    def _get_request(self, url: str = "", query_params: Dict[str, Any] = {}, headers: Dict[str, Any] = {}, auth_token: str = "", **kwargs) -> Tuple[Optional[dict], dict, int]:
        "make a generic GET request"
        if len(auth_token):
            headers = self.set_request_token(headers, auth_token)

        try:
            resp: requests.Response = requests.get(url, headers=headers, params=query_params)
            resp_headers = dict(resp.headers)

            if len(resp.text):
                if "Content-Type" in resp_headers:
                    resp_body: Optional[Dict[str, Any]] = self._decode_response_body(resp_headers["Content-Type"], resp.text)
                else:
                    # assume it is json as its most common mime type
                    resp_body = resp.json()
            else:
                resp_body = None

            return resp_body, resp_headers, resp.status_code
        except Exception as ex:
            raise RuntimeError(str(ex))

    def _post_request(self, url: str = "", query_params: Dict[str, Any] = {}, headers: Dict[str, Any] = {}, auth_token: str = "", content_type: str = "", body: Dict[str, Any] = {}) -> Tuple[Optional[dict], dict, int]:
        "make a generic POST request"
        if len(auth_token):
            headers = self.set_request_token(headers, auth_token)

        encoded_body = self._encode_request_body(content_type, body)
        headers['Content-Type'] = content_type

        try:
            resp: requests.Response = requests.post(url, headers=headers, data=encoded_body)
            resp_headers = dict(resp.headers)

            if len(resp.text):
                if "Content-Type" in resp_headers:
                    resp_body: Optional[Dict[str, Any]] = self._decode_response_body(resp_headers["Content-Type"], resp.text)
                else:
                    # assume it is json as its most common mime type
                    resp_body = resp.json()
            else:
                resp_body = None

            return resp_body, resp_headers, resp.status_code
        except Exception as ex:
            raise RuntimeError(str(ex))

    def _delete_request(self, url: str = "", query_params: Dict[str, Any] = {}, headers: Dict[str, Any] = {}, auth_token: str = "", **kwargs) -> Tuple[Optional[dict], dict, int]:
        "make a generic DELETE request"
        if len(auth_token):
            headers = self.set_request_token(headers, auth_token)

        try:
            resp: requests.Response = requests.delete(url, headers=headers, params=query_params)
            resp_headers = dict(resp.headers)

            if len(resp.text):
                if "Content-Type" in resp_headers:
                    resp_body: Optional[Dict[str, Any]] = self._decode_response_body(resp_headers["Content-Type"], resp.text)

                    if resp_body == None:
                        err = "Error Decoding JSON Response"
                else:
                    # assume it is json as its most common mime type
                    resp_body = resp.json()
            else:
                resp_body = None

            return resp_body, resp_headers, resp.status_code
        except Exception as ex:
            raise RuntimeError(str(ex))

    def _put_request(self, url: str = "", query_params: Dict[str, Any] = {}, headers: Dict[str, Any] = {}, auth_token: str = "", content_type: str = "", body: Dict[str, Any] = {}) -> Tuple[Optional[dict], dict, int]:
        "make a generic PUT request"
        if len(auth_token):
            headers = self.set_request_token(headers, auth_token)

        encoded_body = self._encode_request_body(content_type, body)
        headers['Content-Type'] = content_type

        try:
            resp: requests.Response = requests.put(url, headers=headers, data=body)
            resp_headers = dict(resp.headers)

            if len(resp.text):
                if "Content-Type" in resp_headers:
                    resp_body: Optional[Dict[str, Any]] = self._decode_response_body(resp_headers["Content-Type"], resp.text)
                else:
                    # assume it is json as its most common mime type
                    resp_body = resp.json()
            else:
                resp_body = None

            return resp_body, resp_headers, resp.status_code

        except Exception as ex:
            raise RuntimeError(str(ex))
