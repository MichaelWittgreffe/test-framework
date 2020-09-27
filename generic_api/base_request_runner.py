import requests
import json


class RequestRunner():
    """
    Base class for executing generic HTTP/1.1 requests
    To derive from this class you must implement the 'authenticate' and 'set_request_token' methods
        if you just to run no-auth requests you can use the base class
    """
    auth_url = ''                   # contains the url used for getting an auth token
    username = ''                   # contains the username used to get an auth token
    password = ''                   # contains the password used to get an auth token
    supported_methods = {}          # dict containing a list of supported HTTP methods
    supported_content_types = {}    # dict containing a list of supported mime types

    def __init__(self, auth_url='', username='', password=''):
        "default constructor"
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.supported_methods = {
            "GET": self._get_request,
            "POST": self._post_request,
            "DELETE": self._delete_request,
            "PUT": self._put_request,
        }
        self.supported_content_types = {
            "application/json": {
                "encode": self._encode_data_to_json,
                "decode": self._decode_json_to_data,
            },
            "application/json; charset=UTF-8": {
                "encode": self._encode_data_to_json,
                "decode": self._decode_json_to_data,
            }
        }

    def authenticate(self):
        "method for authenticating with the configured authentication schema - derived classes should override this"
        auth_token = ""             # Must return a string authentication token.
        return auth_token

    def set_request_token(self, request_headers, auth_token):
        "method to set the authentication token in the request headers. Should be overridden by derived classes"
        result_header = {}          # Must return the expected request header as a dict, with the authentication token set.
                                   # At this point, no other request headers have been set.
        return result_header

    def run_request(self, method, url, content_type='', body={}, query_params={}, header_params={}, authenticate=True):
        "run an HTTP/1.1 request"
        if len(method) and method in self.supported_methods:
            runner = self.supported_methods[method.upper()]

            if authenticate:
                if not (self.auth_url) or not len(self.username) or not len(self.password):
                    raise ValueError("Authentication Details Not Populated")

                auth_token = self.authenticate()

                if len(auth_token):
                    return runner(url=url, content_type=content_type, body=body, query_params=query_params, auth_token=auth_token, header_params=header_params)
                raise ValueError("Returned Auth Token Is Empty")
            else:
                return runner(url=url, content_type=content_type, body=body, query_params=query_params, header_params=header_params)
        else:
            raise ValueError("Method " + method + " Not Supported Or Invalid")

    def _encode_request_body(self, content_type, request_data):
        "encodes and returns the body for the request if the content_type is supported"
        if request_data != None:
            type_data = self.supported_content_types[content_type]
            encoder = type_data['encode']
            return content_type, encoder(request_data)
        raise ValueError("request_data Is None")

    def _decode_response_body(self, resp_content_type, resp_data):
        "decodes a response body from the returned MIME type to a Python data structure"
        if resp_content_type in self.supported_content_types:
            type_data = self.supported_content_types[resp_content_type]
            decoder = type_data['decode']
            return resp_content_type, decoder(resp_data)
        raise ValueError("Response Content-Type Is Not Supported: " + resp_content_type)

    def _encode_data_to_json(self, data):
        "encodes the given dict to a json string"
        result = None

        if isinstance(data, dict):
            try:
                result = json.dumps(data)
            except Exception as ex:
                result = None

        return result

    def _decode_json_to_data(self, raw_json):
        "decodes the given json string to a dict"
        result = None

        if isinstance(raw_json, str):
            try:
                result = json.loads(raw_json)
            except Exception as ex:
                result = None

        return result

    def _get_request(self, **kwargs):
        "make a generic GET request"
        resp_body = None
        resp_headers = None
        status_code = -1
        err = ""

        if 'url' in kwargs and 'query_params' in kwargs:
            url = kwargs.get('url')
            query_params = kwargs.get('query_params')
            headers = kwargs.get('header_params')

            if 'auth_token' in kwargs:
                headers = self.set_request_token(headers, kwargs.get('auth_token'))

            try:
                resp = requests.get(url, headers=headers, params=query_params)
                resp_headers = resp.headers
                status_code = resp.status_code

                if len(resp.text):
                    if "Content-Type" in resp_headers:
                        _, resp_body = self._decode_response_body(resp_headers["Content-Type"], resp.text)

                        if resp_body == None:
                            err = "Error Decoding JSON Response"
                    else:
                        # assume it is json as its most common mime type
                        resp_body = resp.json()
                else:
                    resp_body = {}
            except Exception as ex:
                err = "Exception: " + ex.__str__()

        return resp_body, resp_headers, status_code, err

    def _post_request(self, **kwargs):
        "make a generic POST request"
        resp_body = None
        resp_headers = None
        status_code = -1
        err = ""

        if 'url' in kwargs and 'content_type' in kwargs and 'body' in kwargs:
            url = kwargs.get('url')
            headers = kwargs.get('header_params')

            if 'auth_token' in kwargs:
                headers = self.set_request_token(headers, kwargs.get('auth_token'))

            content_type, body = self._encode_request_body(kwargs.get('content_type'), kwargs.get('body'))

            if body != None:
                headers['Content-Type'] = content_type

                try:
                    resp = requests.post(url, headers=headers, data=body)
                    resp_headers = resp.headers
                    status_code = resp.status_code

                    if len(resp.text):
                        if "Content-Type" in resp_headers:
                            _, resp_body = self._decode_response_body(resp_headers["Content-Type"], resp.text)

                            if resp_body == None:
                                err = "Error Decoding JSON Response"
                        else:
                            # assume it is json as its most common mime type
                            resp_body = resp.json()
                    else:
                        resp_body = {}
                except Exception as ex:
                    err = "Exception: " + ex.__str__()
            else:
                err = "Error Encoding Body"

        return resp_body, resp_headers, status_code, err

    def _delete_request(self, **kwargs):
        "make a generic DELETE request"
        resp_body = None
        resp_headers = None
        status_code = -1
        err = ""

        if 'url' in kwargs and 'query_params' in kwargs:
            url = kwargs.get('url')
            query_params = kwargs.get('query_params')
            headers = kwargs.get('header_params')

            if 'auth_token' in kwargs:
                headers = self.set_request_token(headers, kwargs.get('auth_token'))

            try:
                resp = requests.delete(url, headers=headers, params=query_params)
                resp_headers = resp.headers
                status_code = resp.status_code

                if len(resp.text):
                    if "Content-Type" in resp_headers:
                        _, resp_body = self._decode_response_body(resp_headers["Content-Type"], resp.text)

                        if resp_body == None:
                            err = "Error Decoding JSON Response"
                    else:
                        # assume it is json as its most common mime type
                        resp_body = resp.json()
                else:
                    resp_body = {}
            except Exception as ex:
                err = "Exception: " + ex.__str__()

        return resp_body, resp_headers, status_code, err

    def _put_request(self, **kwargs):
        "make a generic PUT request"
        resp_body = None
        resp_headers = None
        status_code = -1
        err = ""

        if 'url' in kwargs and 'content_type' in kwargs and 'body' in kwargs:
            url = kwargs.get('url')
            headers = kwargs.get('header_params')

            if 'auth_token' in kwargs:
                headers = self.set_request_token(headers, kwargs.get('auth_token'))

            content_type, body = self._encode_request_body(kwargs.get('content_type'), kwargs.get('body'))

            if body != None:
                headers['Content-Type'] = content_type

                try:
                    resp = requests.put(url, headers=headers, data=body)
                    resp_headers = resp.headers
                    status_code = resp.status_code

                    if len(resp.text):
                        if "Content-Type" in resp_headers:
                            _, resp_body = self._decode_response_body(resp_headers["Content-Type"], resp.text)

                            if resp_body == None:
                                err = "Error Decoding JSON Response"
                        else:
                            # assume it is json as its most common mime type
                            resp_body = resp.json()
                    else:
                        resp_body = {}
                except Exception as ex:
                    err = "Exception: " + ex.__str__()
            else:
                err = "Error Encoding Body"

        return resp_body, resp_headers, status_code, err
